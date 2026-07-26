"""
Retraining Service for Earthwise AI Poultry FCR Advisor
========================================================
Handles model retraining when new data is uploaded.

WARNING: In production, this endpoint MUST require authentication
and rate limiting. For this university demonstration, it is
unauthenticated.
"""

import logging
import shutil
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)

# Paths
API_DIR = Path(__file__).resolve().parent
MODELS_DIR = API_DIR.parent / "linear_regression" / "models"
DATA_DIR = API_DIR.parent / "linear_regression" / "data"
BACKUP_DIR = MODELS_DIR / "backup"

# Feature configuration
BASE_FEATURES = ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent']
ENGINEERED_FEATURES = ['survival_rate', 'weight_gain_per_day', 'harvest_efficiency', 'mortality_weight_interaction']
ALL_FEATURES = BASE_FEATURES + ENGINEERED_FEATURES
TARGET_COL = 'fcr'

# Required columns in uploaded CSV (base features only; FCR will be derived)
REQUIRED_UPLOAD_COLUMNS = ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent']

# Also accept the original Indonesian column names
COLUMN_MAPPING = {
    'Umur': 'age_days',
    'BW': 'body_weight_kg',
    '%Panen': 'harvest_percent',
    'Deplesi': 'mortality_percent',
    'IP': 'production_index'
}


def validate_uploaded_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """
    Validate uploaded CSV data for retraining.

    Parameters:
        df: DataFrame from uploaded CSV.

    Returns:
        Tuple of (cleaned DataFrame, list of warnings).
    """
    warnings_list = []

    # Rename Indonesian columns if present
    df = df.rename(columns=COLUMN_MAPPING)

    # Check for production_index to derive FCR
    has_production_index = 'production_index' in df.columns
    has_fcr = 'fcr' in df.columns

    # Check required base columns
    missing_cols = [col for col in REQUIRED_UPLOAD_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}. "
                         f"Required: {REQUIRED_UPLOAD_COLUMNS}")

    # Derive FCR if not present
    if not has_fcr:
        if has_production_index:
            # Derive from IP formula
            df['livability_percent'] = 100 - df['mortality_percent']
            df['bw_grams'] = df['body_weight_kg'] * 1000
            df['fcr'] = (df['livability_percent'] * df['bw_grams']) / (
                df['production_index'] * df['age_days'] * 10
            )
            df = df.drop(columns=['livability_percent', 'bw_grams', 'production_index'], errors='ignore')
            warnings_list.append("FCR derived from production_index using standard IP formula.")
        else:
            raise ValueError(
                "Neither 'fcr' nor 'production_index' (IP) column found. "
                "Cannot compute target variable. Please include either 'fcr' "
                "or 'production_index' in your data."
            )

    # Drop non-feature columns
    keep_cols = BASE_FEATURES + ['fcr']
    extra_cols = [col for col in df.columns if col not in keep_cols]
    if extra_cols:
        df = df.drop(columns=extra_cols, errors='ignore')
        warnings_list.append(f"Dropped extra columns: {extra_cols}")

    # Validate data types
    for col in BASE_FEATURES + ['fcr']:
        if not pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                warnings_list.append(f"Converted {col} to numeric (some values may be NaN).")
            except Exception:
                raise ValueError(f"Column '{col}' contains non-numeric values that cannot be converted.")

    # Drop rows with NaN
    initial_rows = len(df)
    df = df.dropna().reset_index(drop=True)
    if len(df) < initial_rows:
        warnings_list.append(f"Dropped {initial_rows - len(df)} rows with missing values.")

    # Drop duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        warnings_list.append(f"Dropped {dup_count} duplicate rows.")

    # Range validation
    range_checks = {
        'age_days': (10, 60),
        'body_weight_kg': (0.1, 5.0),
        'harvest_percent': (0, 100),
        'mortality_percent': (0, 100),
        'fcr': (0.5, 5.0),
    }
    for col, (min_val, max_val) in range_checks.items():
        outliers = ((df[col] < min_val) | (df[col] > max_val)).sum()
        if outliers > 0:
            warnings_list.append(
                f"Column '{col}' has {outliers} values outside expected range "
                f"({min_val}-{max_val}). These rows are kept but may affect model quality."
            )

    if len(df) < 10:
        raise ValueError(f"After cleaning, only {len(df)} valid rows remain. "
                         f"Minimum 10 rows required for retraining.")

    return df, warnings_list


def engineer_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to a DataFrame."""
    df = df.copy()
    df['survival_rate'] = 100 - df['mortality_percent']
    df['weight_gain_per_day'] = df['body_weight_kg'] / df['age_days']
    df['harvest_efficiency'] = df['harvest_percent'] / df['age_days']
    df['mortality_weight_interaction'] = df['mortality_percent'] * df['body_weight_kg']
    return df


def retrain_models(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Retrain all candidate models and select the best one.

    Process:
    1. Backup current model
    2. Engineer features
    3. Split data
    4. Train all 4 models
    5. Evaluate
    6. Replace model only if new one is acceptable
    7. Return before/after metrics

    Parameters:
        df: Cleaned DataFrame with base features + fcr.

    Returns:
        Dictionary with retraining results.
    """
    # Step 1: Load current model metrics for comparison
    old_metadata = {}
    metadata_path = MODELS_DIR / 'model_metadata.json'
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            old_metadata = json.load(f)

    old_metrics = old_metadata.get('metrics', {})

    # Step 2: Backup current model
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    for file_name in ['best_model.joblib', 'preprocessor.joblib', 'model_metadata.json']:
        src = MODELS_DIR / file_name
        if src.exists():
            dst = BACKUP_DIR / f"{timestamp}_{file_name}"
            shutil.copy2(src, dst)
    logger.info(f"Model backup created with timestamp {timestamp}")

    # Step 3: Engineer features
    df = engineer_features_df(df)

    X = df[ALL_FEATURES]
    y = df[TARGET_COL]

    # Step 4: Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Step 5: Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[('num', StandardScaler(), ALL_FEATURES)],
        remainder='passthrough'
    )
    X_train_scaled = preprocessor.fit_transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)

    # Step 6: Train all 4 models
    models = {
        'Linear Regression': LinearRegression(),
        'SGD Regressor': SGDRegressor(
            loss='squared_error', penalty='l2', alpha=0.001,
            learning_rate='invscaling', eta0=0.01, max_iter=500,
            random_state=42, tol=1e-4
        ),
        'Decision Tree': DecisionTreeRegressor(random_state=42, max_depth=10),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
    }

    model_results = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred_test = model.predict(X_test_scaled)
        y_pred_train = model.predict(X_train_scaled)

        test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
        train_rmse = float(np.sqrt(mean_squared_error(y_train, y_pred_train)))
        test_mae = float(mean_absolute_error(y_test, y_pred_test))
        test_mse = float(mean_squared_error(y_test, y_pred_test))
        test_r2 = float(r2_score(y_test, y_pred_test))

        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5,
                                    scoring='neg_root_mean_squared_error')
        cv_rmse = float(-cv_scores.mean())

        model_results[name] = {
            'model': model,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'test_mse': test_mse,
            'test_r2': test_r2,
            'cv_rmse': cv_rmse,
        }
        logger.info(f"  {name}: Test RMSE={test_rmse:.4f}, R²={test_r2:.4f}")

    # Step 7: Select best model
    best_name = min(model_results, key=lambda k: model_results[k]['test_rmse'])
    best_result = model_results[best_name]
    best_model = best_result['model']

    new_metrics = {
        'test_rmse': round(best_result['test_rmse'], 4),
        'test_mae': round(best_result['test_mae'], 4),
        'test_mse': round(best_result['test_mse'], 6),
        'test_r2': round(best_result['test_r2'], 4),
        'cv_rmse': round(best_result['cv_rmse'], 4),
        'train_rmse': round(best_result['train_rmse'], 4),
    }

    # Step 8: Save new model (atomic replacement)
    new_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', best_model)
    ])

    joblib.dump(new_pipeline, MODELS_DIR / 'best_model.joblib')
    joblib.dump(preprocessor, MODELS_DIR / 'preprocessor.joblib')

    new_version = f"2.0.0-retrained-{timestamp}"
    new_metadata = {
        'model_name': best_name,
        'model_version': new_version,
        'target': TARGET_COL,
        'features': ALL_FEATURES,
        'base_features': BASE_FEATURES,
        'engineered_features': ENGINEERED_FEATURES,
        'training_date': datetime.now().isoformat(),
        'training_samples': int(X_train.shape[0]),
        'test_samples': int(X_test.shape[0]),
        'total_data_rows': int(len(df)),
        'metrics': new_metrics,
        'all_model_results': {
            name: {
                'test_rmse': round(res['test_rmse'], 4),
                'test_mae': round(res['test_mae'], 4),
                'test_r2': round(res['test_r2'], 4),
                'cv_rmse': round(res['cv_rmse'], 4),
            }
            for name, res in model_results.items()
        }
    }

    with open(metadata_path, 'w') as f:
        json.dump(new_metadata, f, indent=2)

    logger.info(f"New best model: {best_name} (version {new_version})")

    return {
        'status': 'success',
        'message': f'Model retrained successfully. Best model: {best_name}',
        'model_version': new_version,
        'best_model': best_name,
        'training_samples': int(X_train.shape[0]),
        'test_samples': int(X_test.shape[0]),
        'old_metrics': old_metrics,
        'new_metrics': new_metrics,
        'all_models_compared': {
            name: {
                'test_rmse': round(res['test_rmse'], 4),
                'test_r2': round(res['test_r2'], 4),
            }
            for name, res in model_results.items()
        },
        'backup_timestamp': timestamp,
    }

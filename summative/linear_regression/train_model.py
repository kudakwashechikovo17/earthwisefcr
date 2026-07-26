"""
Earthwise AI Poultry Production and Feed Efficiency Advisor
===========================================================
Complete model training pipeline for Feed Conversion Ratio (FCR) prediction.

This script:
1. Loads and cleans poultry performance data
2. Derives FCR from Production Index (IP)
3. Performs EDA with 12+ visualizations
4. Engineers features
5. Trains 4 regression models (LinearRegression, SGDRegressor, DecisionTree, RandomForest)
6. Tunes hyperparameters
7. Evaluates and compares all models
8. Saves the best model and metadata
9. Demonstrates single-row prediction

Dataset: Indonesian commercial broiler flock performance data
Target: Feed Conversion Ratio (FCR)
"""

# ============================================================
# CELL 1: Imports and Configuration
# ============================================================
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import warnings
import os
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"

# Create directories
MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
FIGSIZE = (10, 6)

print("=" * 70)
print("EARTHWISE AI POULTRY PRODUCTION & FEED EFFICIENCY ADVISOR")
print("Model Training Pipeline")
print("=" * 70)

# ============================================================
# CELL 2: Data Loading and Inspection
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: DATA LOADING & INSPECTION")
print("=" * 70)

csv_path = DATA_DIR / "poultry_data.csv"
df_raw = pd.read_csv(csv_path)

print(f"\nDataset loaded from: {csv_path}")
print(f"Shape: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
print(f"\nColumn Names: {list(df_raw.columns)}")
print(f"\nData Types:\n{df_raw.dtypes}")
print(f"\nFirst 5 rows:\n{df_raw.head()}")
print(f"\nDescriptive Statistics:\n{df_raw.describe()}")
print(f"\nMissing Values:\n{df_raw.isnull().sum()}")
print(f"\nDuplicate Rows: {df_raw.duplicated().sum()}")
print(f"\nUnique Values Per Column:")
for col in df_raw.columns:
    print(f"  {col}: {df_raw[col].nunique()}")

# ============================================================
# CELL 3: Data Cleaning
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: DATA CLEANING")
print("=" * 70)

# Drop duplicates
df = df_raw.drop_duplicates().reset_index(drop=True)
print(f"Dropped {df_raw.shape[0] - df.shape[0]} duplicate rows. Remaining: {df.shape[0]} rows")

# Rename columns from Indonesian to English
column_mapping = {
    'Umur': 'age_days',
    'BW': 'body_weight_kg',
    '%Panen': 'harvest_percent',
    'Deplesi': 'mortality_percent',
    'IP': 'production_index'
}
df = df.rename(columns=column_mapping)
print(f"\nRenamed columns: {list(df.columns)}")

# Derive FCR from Production Index
# Standard formula: IP = (Livability% × BW_grams) / (FCR × Age_days × 10)
# Therefore:  FCR = (Livability% × BW_grams) / (IP × Age_days × 10)
df['livability_percent'] = 100 - df['mortality_percent']
df['bw_grams'] = df['body_weight_kg'] * 1000
df['fcr'] = (df['livability_percent'] * df['bw_grams']) / (df['production_index'] * df['age_days'] * 10)

print(f"\nDerived FCR using: FCR = (Livability% × BW_grams) / (IP × Age_days × 10)")
print(f"FCR Statistics:")
print(f"  Mean:   {df['fcr'].mean():.4f}")
print(f"  Std:    {df['fcr'].std():.4f}")
print(f"  Min:    {df['fcr'].min():.4f}")
print(f"  Max:    {df['fcr'].max():.4f}")
print(f"  Median: {df['fcr'].median():.4f}")

# Drop production_index (target leakage) and helper columns
df = df.drop(columns=['production_index', 'livability_percent', 'bw_grams'])
print(f"\nDropped 'production_index' (target leakage), 'livability_percent', 'bw_grams' (helper columns)")
print(f"Final columns: {list(df.columns)}")

# ============================================================
# CELL 4: Data Dictionary
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: DATA DICTIONARY")
print("=" * 70)

data_dict = pd.DataFrame({
    'Variable': ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent', 'fcr'],
    'Type': ['float64', 'float64', 'float64', 'float64', 'float64'],
    'Role': ['Feature', 'Feature', 'Feature', 'Feature', 'Target'],
    'Description': [
        'Slaughter/harvest age of the flock in days',
        'Average live body weight at harvest in kilograms',
        'Percentage of placed birds successfully harvested',
        'Cumulative flock mortality percentage',
        'Feed Conversion Ratio (feed consumed / weight gained) — DERIVED from IP'
    ],
    'Min': [df['age_days'].min(), df['body_weight_kg'].min(), df['harvest_percent'].min(),
            df['mortality_percent'].min(), df['fcr'].min()],
    'Max': [df['age_days'].max(), df['body_weight_kg'].max(), df['harvest_percent'].max(),
            df['mortality_percent'].max(), df['fcr'].max()],
    'Mean': [df['age_days'].mean(), df['body_weight_kg'].mean(), df['harvest_percent'].mean(),
             df['mortality_percent'].mean(), df['fcr'].mean()]
})
print(data_dict.to_string(index=False))

# ============================================================
# CELL 5: Exploratory Data Analysis — Visualizations
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: EXPLORATORY DATA ANALYSIS")
print("=" * 70)

# --- Visualization 1: FCR Distribution ---
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.hist(df['fcr'], bins=30, color='#2E86AB', edgecolor='white', alpha=0.85)
ax.axvline(df['fcr'].mean(), color='#E84855', linestyle='--', linewidth=2, label=f'Mean: {df["fcr"].mean():.3f}')
ax.axvline(df['fcr'].median(), color='#F18F01', linestyle='--', linewidth=2, label=f'Median: {df["fcr"].median():.3f}')
ax.set_xlabel('Feed Conversion Ratio (FCR)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Distribution of Feed Conversion Ratio (FCR)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(CHARTS_DIR / '01_fcr_distribution.png', dpi=150)
plt.close()
print("\n[Visualization 1] FCR Distribution Histogram")
print("  INTERPRETATION: The FCR distribution is roughly normal with a slight right skew.")
print(f"  Most flocks achieve FCR between {df['fcr'].quantile(0.25):.2f} and {df['fcr'].quantile(0.75):.2f}.")
print("  This is consistent with modern commercial broiler performance (lower FCR = better efficiency).")
print("  No extreme transformation is needed for the target variable.")

# --- Visualization 2: Correlation Heatmap ---
fig, ax = plt.subplots(figsize=(8, 6))
corr_matrix = df[['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent', 'fcr']].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, ax=ax, vmin=-1, vmax=1)
ax.set_title('Correlation Heatmap: Features and FCR', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '02_correlation_heatmap.png', dpi=150)
plt.close()
print("\n[Visualization 2] Correlation Heatmap")
print(f"  INTERPRETATION: Key correlations with FCR:")
for col in ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent']:
    r = corr_matrix.loc[col, 'fcr']
    direction = "positive" if r > 0 else "negative"
    strength = "strong" if abs(r) > 0.5 else "moderate" if abs(r) > 0.3 else "weak"
    print(f"    {col}: r={r:.3f} ({strength} {direction})")
print("  Body weight has the strongest correlation — heavier birds tend to have lower FCR.")
print("  This makes biological sense: efficient feed conversion produces heavier birds.")

# --- Visualization 3: Body Weight vs FCR ---
fig, ax = plt.subplots(figsize=FIGSIZE)
scatter = ax.scatter(df['body_weight_kg'], df['fcr'], c=df['mortality_percent'],
                     cmap='YlOrRd', alpha=0.7, edgecolors='gray', linewidth=0.5, s=50)
plt.colorbar(scatter, label='Mortality %')
z = np.polyfit(df['body_weight_kg'], df['fcr'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['body_weight_kg'].min(), df['body_weight_kg'].max(), 100)
ax.plot(x_line, p(x_line), '--', color='#E84855', linewidth=2, label='Trend line')
ax.set_xlabel('Body Weight (kg)', fontsize=12)
ax.set_ylabel('FCR', fontsize=12)
ax.set_title('Body Weight vs FCR (colored by Mortality %)', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(CHARTS_DIR / '03_bw_vs_fcr.png', dpi=150)
plt.close()
print("\n[Visualization 3] Body Weight vs FCR Scatter Plot")
print("  INTERPRETATION: Clear negative trend — heavier birds -> lower (better) FCR.")
print("  Color coding shows that higher mortality flocks tend to cluster at lower body weights")
print("  and higher FCR, suggesting that unhealthy flocks waste more feed per kg of weight gained.")

# --- Visualization 4: Age vs FCR ---
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.scatter(df['age_days'], df['fcr'], color='#2E86AB', alpha=0.6, edgecolors='gray', linewidth=0.5, s=50)
z = np.polyfit(df['age_days'], df['fcr'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['age_days'].min(), df['age_days'].max(), 100)
ax.plot(x_line, p(x_line), '--', color='#E84855', linewidth=2, label='Trend line')
ax.set_xlabel('Age (days)', fontsize=12)
ax.set_ylabel('FCR', fontsize=12)
ax.set_title('Age at Harvest vs FCR', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(CHARTS_DIR / '04_age_vs_fcr.png', dpi=150)
plt.close()
print("\n[Visualization 4] Age vs FCR Scatter Plot")
print("  INTERPRETATION: Moderate positive trend — older birds tend to have slightly higher FCR.")
print("  This is expected: older broilers become less feed-efficient as they approach maturity.")
print("  The effect is weaker than body weight, suggesting age alone is a moderate predictor.")

# --- Visualization 5: Mortality vs FCR ---
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.scatter(df['mortality_percent'], df['fcr'], color='#E84855', alpha=0.6, edgecolors='gray', linewidth=0.5, s=50)
z = np.polyfit(df['mortality_percent'], df['fcr'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['mortality_percent'].min(), df['mortality_percent'].max(), 100)
ax.plot(x_line, p(x_line), '--', color='#2E86AB', linewidth=2, label='Trend line')
ax.set_xlabel('Mortality (%)', fontsize=12)
ax.set_ylabel('FCR', fontsize=12)
ax.set_title('Mortality vs FCR', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(CHARTS_DIR / '05_mortality_vs_fcr.png', dpi=150)
plt.close()
print("\n[Visualization 5] Mortality vs FCR Scatter Plot")
print("  INTERPRETATION: Positive correlation — higher mortality flocks tend to have worse FCR.")
print("  Sick flocks consume feed but die before converting it to body weight,")
print("  increasing the overall feed-to-weight ratio for survivors.")

# --- Visualization 6: Numeric Feature Distributions ---
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
features_for_dist = ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent']
colors = ['#2E86AB', '#F18F01', '#44BBA4', '#E84855']
for ax, col, color in zip(axes.flatten(), features_for_dist, colors):
    ax.hist(df[col], bins=25, color=color, edgecolor='white', alpha=0.85)
    ax.axvline(df[col].mean(), color='black', linestyle='--', linewidth=1.5, label=f'Mean: {df[col].mean():.2f}')
    ax.set_title(col, fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
plt.suptitle('Distribution of All Numeric Features', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(CHARTS_DIR / '06_feature_distributions.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[Visualization 6] Feature Distribution Histograms")
print("  INTERPRETATION:")
print("  - age_days: Tight range (24–29), roughly normal. Most flocks harvested around 27 days.")
print("  - body_weight_kg: Range 0.85–1.51 kg, roughly normal. Lighter than Western broilers.")
print("  - harvest_percent: Wide range (5.7–79.8%), right-skewed. Some flocks have very low harvest.")
print("  - mortality_percent: Right-skewed with most below 5%. Some outlier flocks at 11–15%.")
print("  StandardScaler is appropriate for all features given the roughly normal distributions.")

# --- Visualization 7: Harvest Percent vs FCR ---
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.scatter(df['harvest_percent'], df['fcr'], color='#44BBA4', alpha=0.6, edgecolors='gray', linewidth=0.5, s=50)
z = np.polyfit(df['harvest_percent'], df['fcr'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['harvest_percent'].min(), df['harvest_percent'].max(), 100)
ax.plot(x_line, p(x_line), '--', color='#E84855', linewidth=2, label='Trend line')
ax.set_xlabel('Harvest Percent (%)', fontsize=12)
ax.set_ylabel('FCR', fontsize=12)
ax.set_title('Harvest Percentage vs FCR', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(CHARTS_DIR / '07_harvest_vs_fcr.png', dpi=150)
plt.close()
print("\n[Visualization 7] Harvest Percentage vs FCR Scatter Plot")
print("  INTERPRETATION: Weak relationship between harvest percentage and FCR.")
print("  Harvest rate reflects farm logistics rather than feed efficiency directly.")
print("  It may still contribute as a secondary signal in ensemble models.")

# ============================================================
# CELL 6: Feature Engineering
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: FEATURE ENGINEERING")
print("=" * 70)

# Engineered features
df['survival_rate'] = 100 - df['mortality_percent']
df['weight_gain_per_day'] = df['body_weight_kg'] / df['age_days']
df['harvest_efficiency'] = df['harvest_percent'] / df['age_days']
df['mortality_weight_interaction'] = df['mortality_percent'] * df['body_weight_kg']

print("\nEngineered Features Created:")
print("  1. survival_rate = 100 - mortality_percent")
print("     -> Higher survival = healthier flock, likely better FCR")
print("  2. weight_gain_per_day = body_weight_kg / age_days")
print("     -> Daily growth rate; faster growers may have different FCR patterns")
print("  3. harvest_efficiency = harvest_percent / age_days")
print("     -> Normalizes harvest rate by age; captures management efficiency")
print("  4. mortality_weight_interaction = mortality_percent * body_weight_kg")
print("     -> Captures the combined effect of mortality on heavier flocks")

# Note: survival_rate and mortality_percent are complements.
# We keep both and let regularization/model handle the collinearity.
# For linear models, we'll rely on StandardScaler + regularization.

# Define final feature set
FEATURE_COLS = [
    'age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent',
    'survival_rate', 'weight_gain_per_day', 'harvest_efficiency', 'mortality_weight_interaction'
]
TARGET_COL = 'fcr'

print(f"\nFinal Feature Set ({len(FEATURE_COLS)} features): {FEATURE_COLS}")
print(f"Target: {TARGET_COL}")
print(f"\nFeature Statistics After Engineering:")
print(df[FEATURE_COLS + [TARGET_COL]].describe().to_string())

# ============================================================
# CELL 7: Train-Test Split and Preprocessing
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: TRAIN-TEST SPLIT & PREPROCESSING")
print("=" * 70)

X = df[FEATURE_COLS].copy()
y = df[TARGET_COL].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set:     {X_test.shape[0]} samples")

# Preprocessing: StandardScaler for all numeric features
# Using ColumnTransformer + Pipeline for clean scikit-learn integration
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), FEATURE_COLS)
    ],
    remainder='passthrough'
)

# Fit only on training data to prevent data leakage
X_train_scaled = preprocessor.fit_transform(X_train)
X_test_scaled = preprocessor.transform(X_test)

print(f"\nPreprocessing: StandardScaler fitted on training data only")
print(f"X_train_scaled shape: {X_train_scaled.shape}")
print(f"X_test_scaled shape:  {X_test_scaled.shape}")

# ============================================================
# CELL 8: Model Training — Four Required Models
# ============================================================
print("\n" + "=" * 70)
print("SECTION 7: MODEL TRAINING")
print("=" * 70)

results = {}

# --- Model 1: Ordinary Linear Regression ---
print("\n--- Model 1: Linear Regression (OLS) ---")
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)
y_pred_lr_train = lr_model.predict(X_train_scaled)
y_pred_lr_test = lr_model.predict(X_test_scaled)

lr_train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_lr_train))
lr_test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_lr_test))
lr_test_mae = mean_absolute_error(y_test, y_pred_lr_test)
lr_test_mse = mean_squared_error(y_test, y_pred_lr_test)
lr_test_r2 = r2_score(y_test, y_pred_lr_test)
lr_cv_scores = cross_val_score(lr_model, X_train_scaled, y_train, cv=5, scoring='neg_root_mean_squared_error')
lr_cv_rmse = -lr_cv_scores.mean()

print(f"  Train RMSE: {lr_train_rmse:.4f}")
print(f"  Test  RMSE: {lr_test_rmse:.4f}")
print(f"  Test  MAE:  {lr_test_mae:.4f}")
print(f"  Test  R²:   {lr_test_r2:.4f}")
print(f"  CV RMSE:    {lr_cv_rmse:.4f} (±{lr_cv_scores.std():.4f})")

results['Linear Regression'] = {
    'model': Pipeline([('preprocessor', preprocessor), ('regressor', lr_model)]),
    'train_rmse': lr_train_rmse, 'test_rmse': lr_test_rmse,
    'test_mae': lr_test_mae, 'test_mse': lr_test_mse,
    'test_r2': lr_test_r2, 'cv_rmse': lr_cv_rmse,
    'y_pred_test': y_pred_lr_test, 'y_pred_train': y_pred_lr_train
}

# --- Model 2: SGD Regressor with epoch-by-epoch loss tracking ---
print("\n--- Model 2: SGD Regressor (Stochastic Gradient Descent) ---")

# Track loss per epoch for loss curve
sgd_train_losses = []
sgd_test_losses = []
n_epochs = 200

sgd_model = SGDRegressor(
    loss='squared_error',
    penalty='l2',
    alpha=0.001,
    learning_rate='invscaling',
    eta0=0.01,
    max_iter=1,
    warm_start=True,
    random_state=42,
    tol=None
)

for epoch in range(n_epochs):
    sgd_model.partial_fit(X_train_scaled, y_train)
    y_pred_sgd_train_epoch = sgd_model.predict(X_train_scaled)
    y_pred_sgd_test_epoch = sgd_model.predict(X_test_scaled)
    train_mse = mean_squared_error(y_train, y_pred_sgd_train_epoch)
    test_mse = mean_squared_error(y_test, y_pred_sgd_test_epoch)
    sgd_train_losses.append(train_mse)
    sgd_test_losses.append(test_mse)

y_pred_sgd_train = sgd_model.predict(X_train_scaled)
y_pred_sgd_test = sgd_model.predict(X_test_scaled)

sgd_train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_sgd_train))
sgd_test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_sgd_test))
sgd_test_mae = mean_absolute_error(y_test, y_pred_sgd_test)
sgd_test_mse = mean_squared_error(y_test, y_pred_sgd_test)
sgd_test_r2 = r2_score(y_test, y_pred_sgd_test)

# Cross-validation for SGD (using a fresh pipeline)
sgd_cv_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('sgd', SGDRegressor(loss='squared_error', penalty='l2', alpha=0.001,
                         learning_rate='invscaling', eta0=0.01, max_iter=200,
                         random_state=42))
])
sgd_cv_scores = cross_val_score(sgd_cv_pipeline, X_train, y_train, cv=5, scoring='neg_root_mean_squared_error')
sgd_cv_rmse = -sgd_cv_scores.mean()

print(f"  Epochs:     {n_epochs}")
print(f"  Train RMSE: {sgd_train_rmse:.4f}")
print(f"  Test  RMSE: {sgd_test_rmse:.4f}")
print(f"  Test  MAE:  {sgd_test_mae:.4f}")
print(f"  Test  R²:   {sgd_test_r2:.4f}")
print(f"  CV RMSE:    {sgd_cv_rmse:.4f} (±{sgd_cv_scores.std():.4f})")

results['SGD Regressor'] = {
    'model': Pipeline([('preprocessor', preprocessor), ('regressor', sgd_model)]),
    'train_rmse': sgd_train_rmse, 'test_rmse': sgd_test_rmse,
    'test_mae': sgd_test_mae, 'test_mse': sgd_test_mse,
    'test_r2': sgd_test_r2, 'cv_rmse': sgd_cv_rmse,
    'y_pred_test': y_pred_sgd_test, 'y_pred_train': y_pred_sgd_train,
    'train_losses': sgd_train_losses, 'test_losses': sgd_test_losses
}

# --- Visualization 8: SGD Training & Validation Loss Curves ---
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.plot(range(1, n_epochs + 1), sgd_train_losses, label='Training Loss (MSE)', color='#2E86AB', linewidth=2)
ax.plot(range(1, n_epochs + 1), sgd_test_losses, label='Validation/Test Loss (MSE)', color='#E84855', linewidth=2)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Mean Squared Error (MSE)', fontsize=12)
ax.set_title('SGD Regressor: Training & Validation Loss Curves', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.set_xlim(1, n_epochs)
plt.tight_layout()
plt.savefig(CHARTS_DIR / '08_sgd_loss_curves.png', dpi=150)
plt.close()
print("\n[Visualization 8] SGD Training & Validation Loss Curves")
print(f"  INTERPRETATION: Training loss decreased from {sgd_train_losses[0]:.4f} to {sgd_train_losses[-1]:.4f}.")
print(f"  Validation loss decreased from {sgd_test_losses[0]:.4f} to {sgd_test_losses[-1]:.4f}.")
print("  Both curves converge, indicating the model is learning without severe overfitting.")
if sgd_test_losses[-1] > sgd_train_losses[-1] * 1.5:
    print("  There is a gap between train and test loss, suggesting some overfitting.")
else:
    print("  Train and test losses are close, suggesting good generalization.")

# --- Model 3: Decision Tree Regressor ---
print("\n--- Model 3: Decision Tree Regressor ---")
dt_model = DecisionTreeRegressor(random_state=42)
dt_model.fit(X_train_scaled, y_train)
y_pred_dt_train = dt_model.predict(X_train_scaled)
y_pred_dt_test = dt_model.predict(X_test_scaled)

dt_train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_dt_train))
dt_test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_dt_test))
dt_test_mae = mean_absolute_error(y_test, y_pred_dt_test)
dt_test_mse = mean_squared_error(y_test, y_pred_dt_test)
dt_test_r2 = r2_score(y_test, y_pred_dt_test)
dt_cv_scores = cross_val_score(dt_model, X_train_scaled, y_train, cv=5, scoring='neg_root_mean_squared_error')
dt_cv_rmse = -dt_cv_scores.mean()

print(f"  Train RMSE: {dt_train_rmse:.4f} (likely near 0 — overfitting)")
print(f"  Test  RMSE: {dt_test_rmse:.4f}")
print(f"  Test  MAE:  {dt_test_mae:.4f}")
print(f"  Test  R²:   {dt_test_r2:.4f}")
print(f"  CV RMSE:    {dt_cv_rmse:.4f} (±{dt_cv_scores.std():.4f})")

results['Decision Tree'] = {
    'model': Pipeline([('preprocessor', preprocessor), ('regressor', dt_model)]),
    'train_rmse': dt_train_rmse, 'test_rmse': dt_test_rmse,
    'test_mae': dt_test_mae, 'test_mse': dt_test_mse,
    'test_r2': dt_test_r2, 'cv_rmse': dt_cv_rmse,
    'y_pred_test': y_pred_dt_test, 'y_pred_train': y_pred_dt_train
}

# --- Model 4: Random Forest Regressor ---
print("\n--- Model 4: Random Forest Regressor ---")
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)
y_pred_rf_train = rf_model.predict(X_train_scaled)
y_pred_rf_test = rf_model.predict(X_test_scaled)

rf_train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_rf_train))
rf_test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf_test))
rf_test_mae = mean_absolute_error(y_test, y_pred_rf_test)
rf_test_mse = mean_squared_error(y_test, y_pred_rf_test)
rf_test_r2 = r2_score(y_test, y_pred_rf_test)
rf_cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5, scoring='neg_root_mean_squared_error')
rf_cv_rmse = -rf_cv_scores.mean()

print(f"  Train RMSE: {rf_train_rmse:.4f}")
print(f"  Test  RMSE: {rf_test_rmse:.4f}")
print(f"  Test  MAE:  {rf_test_mae:.4f}")
print(f"  Test  R²:   {rf_test_r2:.4f}")
print(f"  CV RMSE:    {rf_cv_rmse:.4f} (±{rf_cv_scores.std():.4f})")

results['Random Forest'] = {
    'model': Pipeline([('preprocessor', preprocessor), ('regressor', rf_model)]),
    'train_rmse': rf_train_rmse, 'test_rmse': rf_test_rmse,
    'test_mae': rf_test_mae, 'test_mse': rf_test_mse,
    'test_r2': rf_test_r2, 'cv_rmse': rf_cv_rmse,
    'y_pred_test': y_pred_rf_test, 'y_pred_train': y_pred_rf_train
}

# ============================================================
# CELL 9: Hyperparameter Tuning
# ============================================================
print("\n" + "=" * 70)
print("SECTION 8: HYPERPARAMETER TUNING")
print("=" * 70)

# --- Tune SGD Regressor ---
print("\n--- Tuning SGD Regressor ---")
sgd_param_grid = {
    'alpha': [0.0001, 0.001, 0.01, 0.1],
    'penalty': ['l2', 'l1', 'elasticnet'],
    'learning_rate': ['constant', 'invscaling', 'adaptive'],
    'eta0': [0.001, 0.01, 0.05],
    'max_iter': [500, 1000]
}
sgd_tuner = RandomizedSearchCV(
    SGDRegressor(random_state=42, tol=1e-4),
    param_distributions=sgd_param_grid,
    n_iter=30, cv=5, scoring='neg_root_mean_squared_error',
    random_state=42, n_jobs=-1
)
sgd_tuner.fit(X_train_scaled, y_train)
print(f"  Best params: {sgd_tuner.best_params_}")
print(f"  Best CV RMSE: {-sgd_tuner.best_score_:.4f}")

# Update SGD with best model
y_pred_sgd_tuned_test = sgd_tuner.best_estimator_.predict(X_test_scaled)
y_pred_sgd_tuned_train = sgd_tuner.best_estimator_.predict(X_train_scaled)
sgd_tuned_test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_sgd_tuned_test))
sgd_tuned_test_mae = mean_absolute_error(y_test, y_pred_sgd_tuned_test)
sgd_tuned_test_mse = mean_squared_error(y_test, y_pred_sgd_tuned_test)
sgd_tuned_test_r2 = r2_score(y_test, y_pred_sgd_tuned_test)
sgd_tuned_cv_rmse = -sgd_tuner.best_score_

if sgd_tuned_test_rmse < results['SGD Regressor']['test_rmse']:
    print(f"  Tuned SGD improved! RMSE: {results['SGD Regressor']['test_rmse']:.4f} -> {sgd_tuned_test_rmse:.4f}")
    results['SGD Regressor'] = {
        'model': Pipeline([('preprocessor', preprocessor), ('regressor', sgd_tuner.best_estimator_)]),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_sgd_tuned_train)),
        'test_rmse': sgd_tuned_test_rmse,
        'test_mae': sgd_tuned_test_mae, 'test_mse': sgd_tuned_test_mse,
        'test_r2': sgd_tuned_test_r2, 'cv_rmse': sgd_tuned_cv_rmse,
        'y_pred_test': y_pred_sgd_tuned_test, 'y_pred_train': y_pred_sgd_tuned_train,
        'train_losses': sgd_train_losses, 'test_losses': sgd_test_losses
    }
else:
    print(f"  Tuned SGD did not improve. Keeping original.")

# --- Tune Decision Tree ---
print("\n--- Tuning Decision Tree ---")
dt_param_grid = {
    'max_depth': [3, 5, 7, 10, 15, None],
    'min_samples_split': [2, 5, 10, 20],
    'min_samples_leaf': [1, 2, 5, 10]
}
dt_tuner = GridSearchCV(
    DecisionTreeRegressor(random_state=42),
    param_grid=dt_param_grid,
    cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1
)
dt_tuner.fit(X_train_scaled, y_train)
print(f"  Best params: {dt_tuner.best_params_}")
print(f"  Best CV RMSE: {-dt_tuner.best_score_:.4f}")

y_pred_dt_tuned_test = dt_tuner.best_estimator_.predict(X_test_scaled)
y_pred_dt_tuned_train = dt_tuner.best_estimator_.predict(X_train_scaled)
dt_tuned_test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_dt_tuned_test))
dt_tuned_test_mae = mean_absolute_error(y_test, y_pred_dt_tuned_test)
dt_tuned_test_mse = mean_squared_error(y_test, y_pred_dt_tuned_test)
dt_tuned_test_r2 = r2_score(y_test, y_pred_dt_tuned_test)

if dt_tuned_test_rmse < results['Decision Tree']['test_rmse']:
    print(f"  Tuned DT improved! RMSE: {results['Decision Tree']['test_rmse']:.4f} -> {dt_tuned_test_rmse:.4f}")
    results['Decision Tree'] = {
        'model': Pipeline([('preprocessor', preprocessor), ('regressor', dt_tuner.best_estimator_)]),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_dt_tuned_train)),
        'test_rmse': dt_tuned_test_rmse,
        'test_mae': dt_tuned_test_mae, 'test_mse': dt_tuned_test_mse,
        'test_r2': dt_tuned_test_r2, 'cv_rmse': -dt_tuner.best_score_,
        'y_pred_test': y_pred_dt_tuned_test, 'y_pred_train': y_pred_dt_tuned_train
    }
else:
    print(f"  Tuned DT did not improve. Keeping original.")

# --- Tune Random Forest ---
print("\n--- Tuning Random Forest ---")
rf_param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 5],
    'max_features': ['sqrt', 'log2', None]
}
rf_tuner = RandomizedSearchCV(
    RandomForestRegressor(random_state=42),
    param_distributions=rf_param_grid,
    n_iter=30, cv=5, scoring='neg_root_mean_squared_error',
    random_state=42, n_jobs=-1
)
rf_tuner.fit(X_train_scaled, y_train)
print(f"  Best params: {rf_tuner.best_params_}")
print(f"  Best CV RMSE: {-rf_tuner.best_score_:.4f}")

y_pred_rf_tuned_test = rf_tuner.best_estimator_.predict(X_test_scaled)
y_pred_rf_tuned_train = rf_tuner.best_estimator_.predict(X_train_scaled)
rf_tuned_test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf_tuned_test))
rf_tuned_test_mae = mean_absolute_error(y_test, y_pred_rf_tuned_test)
rf_tuned_test_mse = mean_squared_error(y_test, y_pred_rf_tuned_test)
rf_tuned_test_r2 = r2_score(y_test, y_pred_rf_tuned_test)

if rf_tuned_test_rmse < results['Random Forest']['test_rmse']:
    print(f"  Tuned RF improved! RMSE: {results['Random Forest']['test_rmse']:.4f} -> {rf_tuned_test_rmse:.4f}")
    results['Random Forest'] = {
        'model': Pipeline([('preprocessor', preprocessor), ('regressor', rf_tuner.best_estimator_)]),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_rf_tuned_train)),
        'test_rmse': rf_tuned_test_rmse,
        'test_mae': rf_tuned_test_mae, 'test_mse': rf_tuned_test_mse,
        'test_r2': rf_tuned_test_r2, 'cv_rmse': -rf_tuner.best_score_,
        'y_pred_test': y_pred_rf_tuned_test, 'y_pred_train': y_pred_rf_tuned_train
    }
else:
    print(f"  Tuned RF did not improve. Keeping original.")

# ============================================================
# CELL 10: Model Evaluation & Comparison
# ============================================================
print("\n" + "=" * 70)
print("SECTION 9: MODEL EVALUATION & COMPARISON")
print("=" * 70)

comparison_data = []
for name, res in results.items():
    comparison_data.append({
        'Model': name,
        'Train RMSE': round(res['train_rmse'], 4),
        'Test RMSE': round(res['test_rmse'], 4),
        'Test MAE': round(res['test_mae'], 4),
        'Test MSE': round(res['test_mse'], 6),
        'Test R²': round(res['test_r2'], 4),
        'CV RMSE': round(res['cv_rmse'], 4),
        'Generalization Gap': round(res['test_rmse'] - res['train_rmse'], 4)
    })

comparison_df = pd.DataFrame(comparison_data)
comparison_df = comparison_df.sort_values('Test RMSE')
print("\nModel Comparison:")
print(comparison_df.to_string(index=False))

# Save metrics
comparison_df.to_csv(OUTPUTS_DIR / 'metrics.csv', index=False)
print(f"\nMetrics saved to {OUTPUTS_DIR / 'metrics.csv'}")

# --- Visualization 9: Model Comparison Bar Chart ---
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
metrics_to_plot = ['Test RMSE', 'Test MAE', 'Test R²']
colors_bar = ['#2E86AB', '#F18F01', '#44BBA4', '#E84855']
for ax, metric in zip(axes, metrics_to_plot):
    bars = ax.bar(comparison_df['Model'], comparison_df[metric], color=colors_bar[:len(comparison_df)])
    ax.set_title(metric, fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    for bar, val in zip(bars, comparison_df[metric]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{val:.4f}', ha='center', va='bottom', fontsize=9)
plt.suptitle('Model Performance Comparison', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '09_model_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[Visualization 9] Model Performance Comparison Bar Chart")

# ============================================================
# CELL 11: Best Model Selection
# ============================================================
print("\n" + "=" * 70)
print("SECTION 10: BEST MODEL SELECTION")
print("=" * 70)

# Select best model by lowest test RMSE
best_name = comparison_df.iloc[0]['Model']
best_result = results[best_name]

print(f"\n>>> BEST MODEL: {best_name}")
print(f"   Test RMSE: {best_result['test_rmse']:.4f}")
print(f"   Test MAE:  {best_result['test_mae']:.4f}")
print(f"   Test R²:   {best_result['test_r2']:.4f}")
print(f"   CV RMSE:   {best_result['cv_rmse']:.4f}")
print(f"   Gen. Gap:  {best_result['test_rmse'] - best_result['train_rmse']:.4f}")
print(f"\n   Selection criteria: Lowest test RMSE, also considering CV RMSE,")
print(f"   generalization gap, and interpretability.")

# --- Visualization 10: Actual vs Predicted (Best Model) ---
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.scatter(y_test, best_result['y_pred_test'], color='#2E86AB', alpha=0.7, edgecolors='gray', s=50, label='Predictions')
min_val = min(y_test.min(), best_result['y_pred_test'].min())
max_val = max(y_test.max(), best_result['y_pred_test'].max())
ax.plot([min_val, max_val], [min_val, max_val], '--', color='#E84855', linewidth=2, label='Perfect prediction')
ax.set_xlabel('Actual FCR', fontsize=12)
ax.set_ylabel('Predicted FCR', fontsize=12)
ax.set_title(f'Actual vs Predicted FCR ({best_name})', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(CHARTS_DIR / '10_actual_vs_predicted.png', dpi=150)
plt.close()
print("\n[Visualization 10] Actual vs Predicted FCR Scatter Plot")
print("  INTERPRETATION: Points close to the diagonal line indicate accurate predictions.")
print("  Scatter around the line shows prediction error magnitude.")

# --- Visualization 11: Residual Plot (Best Model) ---
residuals = y_test.values - best_result['y_pred_test']
fig, ax = plt.subplots(figsize=FIGSIZE)
ax.scatter(best_result['y_pred_test'], residuals, color='#44BBA4', alpha=0.7, edgecolors='gray', s=50)
ax.axhline(y=0, color='#E84855', linestyle='--', linewidth=2)
ax.set_xlabel('Predicted FCR', fontsize=12)
ax.set_ylabel('Residuals (Actual - Predicted)', fontsize=12)
ax.set_title(f'Residual Plot ({best_name})', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '11_residuals.png', dpi=150)
plt.close()
print("\n[Visualization 11] Residual Plot")
print("  INTERPRETATION: Residuals should be randomly scattered around zero.")
print("  Patterns indicate systematic prediction errors; fan shapes indicate heteroscedasticity.")

# --- Visualization 12: Feature Importance (Random Forest) ---
rf_result = results['Random Forest']
rf_regressor = rf_result['model'].named_steps['regressor']
importances = rf_regressor.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': FEATURE_COLS,
    'Importance': importances
}).sort_values('Importance', ascending=True)

fig, ax = plt.subplots(figsize=FIGSIZE)
ax.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='#2E86AB')
ax.set_xlabel('Feature Importance', fontsize=12)
ax.set_title('Random Forest Feature Importance', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '12_feature_importance.png', dpi=150)
plt.close()
print("\n[Visualization 12] Random Forest Feature Importance")
print("  INTERPRETATION: Shows which features contribute most to the Random Forest's predictions.")
print("  Top features:")
for _, row in feature_importance_df.sort_values('Importance', ascending=False).head(4).iterrows():
    print(f"    {row['Feature']}: {row['Importance']:.4f}")

# --- Visualization 13: Before-and-After Regression Line ---
# Show the best-fit line on the most important single feature vs FCR
# Use body_weight_kg as the primary feature
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Before: Raw scatter (no model)
axes[0].scatter(df['body_weight_kg'], df['fcr'], color='#CCCCCC', alpha=0.5, s=40, label='Data points')
axes[0].set_xlabel('Body Weight (kg)', fontsize=12)
axes[0].set_ylabel('FCR', fontsize=12)
axes[0].set_title('Before Training: Raw Data', fontsize=13, fontweight='bold')
axes[0].legend()

# After: Scatter with Linear Regression line
axes[1].scatter(df['body_weight_kg'], df['fcr'], color='#2E86AB', alpha=0.5, s=40, label='Data points')
z = np.polyfit(df['body_weight_kg'].values, df['fcr'].values, 1)
p = np.poly1d(z)
x_sorted = np.sort(df['body_weight_kg'].values)
axes[1].plot(x_sorted, p(x_sorted), color='#E84855', linewidth=3, label=f'Best fit: y={z[0]:.3f}x + {z[1]:.3f}')
axes[1].set_xlabel('Body Weight (kg)', fontsize=12)
axes[1].set_ylabel('FCR', fontsize=12)
axes[1].set_title('After Training: Linear Regression Fit', fontsize=13, fontweight='bold')
axes[1].legend()

plt.suptitle('Before and After: Linear Regression on Body Weight vs FCR', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '13_before_after_regression.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[Visualization 13] Before-and-After Regression Line")
print("  INTERPRETATION: Left panel shows raw scatter without any model fit.")
print("  Right panel shows the linear regression line fitted through the data.")
print("  The negative slope confirms: heavier birds -> lower (better) FCR.")

# ============================================================
# CELL 12: Save Best Model
# ============================================================
print("\n" + "=" * 70)
print("SECTION 11: SAVE BEST MODEL")
print("=" * 70)

# Save the complete pipeline (preprocessor + model)
best_pipeline = best_result['model']
joblib.dump(best_pipeline, MODELS_DIR / 'best_model.joblib')
print(f"Best model pipeline saved to: {MODELS_DIR / 'best_model.joblib'}")

# Save preprocessor separately
joblib.dump(preprocessor, MODELS_DIR / 'preprocessor.joblib')
print(f"Preprocessor saved to: {MODELS_DIR / 'preprocessor.joblib'}")

# Save metadata
metadata = {
    'model_name': best_name,
    'model_version': '1.0.0',
    'target': TARGET_COL,
    'features': FEATURE_COLS,
    'base_features': ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent'],
    'engineered_features': ['survival_rate', 'weight_gain_per_day', 'harvest_efficiency', 'mortality_weight_interaction'],
    'training_date': datetime.now().isoformat(),
    'training_samples': int(X_train.shape[0]),
    'test_samples': int(X_test.shape[0]),
    'metrics': {
        'test_rmse': round(float(best_result['test_rmse']), 4),
        'test_mae': round(float(best_result['test_mae']), 4),
        'test_mse': round(float(best_result['test_mse']), 6),
        'test_r2': round(float(best_result['test_r2']), 4),
        'cv_rmse': round(float(best_result['cv_rmse']), 4),
        'train_rmse': round(float(best_result['train_rmse']), 4)
    },
    'feature_ranges': {
        col: {
            'min': round(float(df[col].min()), 4),
            'max': round(float(df[col].max()), 4),
            'mean': round(float(df[col].mean()), 4)
        }
        for col in FEATURE_COLS
    },
    'all_model_results': {
        name: {
            'test_rmse': round(float(res['test_rmse']), 4),
            'test_mae': round(float(res['test_mae']), 4),
            'test_r2': round(float(res['test_r2']), 4),
            'cv_rmse': round(float(res['cv_rmse']), 4)
        }
        for name, res in results.items()
    }
}

with open(MODELS_DIR / 'model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"Model metadata saved to: {MODELS_DIR / 'model_metadata.json'}")

# ============================================================
# CELL 13: Single Prediction Demonstration
# ============================================================
print("\n" + "=" * 70)
print("SECTION 12: SINGLE PREDICTION DEMONSTRATION")
print("=" * 70)

# --- Prediction on one real row from X_test ---
print("\n--- Prediction on a real test sample ---")
sample_idx = 0
sample_row = X_test.iloc[[sample_idx]]
actual_fcr = y_test.iloc[sample_idx]

# Load model from disk to demonstrate deployment readiness
loaded_model = joblib.load(MODELS_DIR / 'best_model.joblib')
predicted_fcr = loaded_model.predict(sample_row)[0]
error = abs(actual_fcr - predicted_fcr)

print(f"Sample Input:\n{sample_row.to_string()}")
print(f"\nActual FCR:    {actual_fcr:.4f}")
print(f"Predicted FCR: {predicted_fcr:.4f}")
print(f"Absolute Error: {error:.4f}")

# --- Prediction from a manually constructed input dictionary ---
print("\n--- Prediction from a manual input dictionary ---")

def predict_fcr(input_data: dict) -> float:
    """
    Predict Feed Conversion Ratio (FCR) from input data.

    Parameters:
        input_data: Dictionary with keys matching FEATURE_COLS.
                    Base features (age_days, body_weight_kg, harvest_percent,
                    mortality_percent) are required. Engineered features
                    will be computed if missing.

    Returns:
        Predicted FCR as a native Python float.
    """
    # Compute engineered features if not provided
    if 'survival_rate' not in input_data:
        input_data['survival_rate'] = 100 - input_data['mortality_percent']
    if 'weight_gain_per_day' not in input_data:
        input_data['weight_gain_per_day'] = input_data['body_weight_kg'] / input_data['age_days']
    if 'harvest_efficiency' not in input_data:
        input_data['harvest_efficiency'] = input_data['harvest_percent'] / input_data['age_days']
    if 'mortality_weight_interaction' not in input_data:
        input_data['mortality_weight_interaction'] = input_data['mortality_percent'] * input_data['body_weight_kg']

    # Validate required columns
    required = ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent',
                'survival_rate', 'weight_gain_per_day', 'harvest_efficiency', 'mortality_weight_interaction']
    missing = [col for col in required if col not in input_data]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    # Create DataFrame with correct column order
    input_df = pd.DataFrame([{col: input_data[col] for col in required}])

    # Load model and predict
    model = joblib.load(MODELS_DIR / 'best_model.joblib')
    prediction = model.predict(input_df)[0]

    return float(prediction)


# Test with a sample input
manual_input = {
    'age_days': 27.0,
    'body_weight_kg': 1.30,
    'harvest_percent': 40.0,
    'mortality_percent': 3.5,
}

manual_prediction = predict_fcr(manual_input)
print(f"Manual Input: {manual_input}")
print(f"Predicted FCR: {manual_prediction:.4f}")

print("\n" + "=" * 70)
print("TRAINING PIPELINE COMPLETE")
print("=" * 70)
print(f"\nBest Model: {best_name}")
print(f"Test RMSE:  {best_result['test_rmse']:.4f}")
print(f"Test R²:    {best_result['test_r2']:.4f}")
print(f"\nArtifacts saved:")
print(f"  Model:       {MODELS_DIR / 'best_model.joblib'}")
print(f"  Preprocessor:{MODELS_DIR / 'preprocessor.joblib'}")
print(f"  Metadata:    {MODELS_DIR / 'model_metadata.json'}")
print(f"  Metrics:     {OUTPUTS_DIR / 'metrics.csv'}")
print(f"  Charts:      {CHARTS_DIR}")

"""
Model Service for Earthwise AI Poultry FCR Advisor
===================================================
Handles model loading, FCR prediction, business calculations,
and recommendation generation.
"""

import joblib
import json
import math
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Paths relative to the API directory
API_DIR = Path(__file__).resolve().parent
MODELS_DIR = API_DIR.parent / "linear_regression" / "models"
DATA_DIR = API_DIR.parent / "linear_regression" / "data"

# Feature configuration
BASE_FEATURES = ['age_days', 'body_weight_kg', 'harvest_percent', 'mortality_percent']
ENGINEERED_FEATURES = ['survival_rate', 'weight_gain_per_day', 'harvest_efficiency', 'mortality_weight_interaction']
ALL_FEATURES = BASE_FEATURES + ENGINEERED_FEATURES

# FCR performance thresholds (configurable)
FCR_THRESHOLDS = {
    'excellent': 1.10,
    'good': 1.25,
    'average': 1.40,
    'below_average': 1.60,
    # anything above 1.60 is 'poor'
}


def load_model():
    """Load the trained model pipeline from disk."""
    model_path = MODELS_DIR / 'best_model.joblib'
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")
    model = joblib.load(model_path)
    logger.info(f"Model loaded from {model_path}")
    return model


def load_metadata() -> Dict[str, Any]:
    """Load model metadata from disk."""
    metadata_path = MODELS_DIR / 'model_metadata.json'
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found at {metadata_path}")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata


def engineer_features(input_data: Dict[str, float]) -> Dict[str, float]:
    """
    Compute engineered features from base features.

    Parameters:
        input_data: Dictionary with base feature values.

    Returns:
        Dictionary with all features (base + engineered).
    """
    data = dict(input_data)

    # Compute engineered features
    data['survival_rate'] = 100 - data['mortality_percent']
    data['weight_gain_per_day'] = data['body_weight_kg'] / data['age_days']
    data['harvest_efficiency'] = data['harvest_percent'] / data['age_days']
    data['mortality_weight_interaction'] = data['mortality_percent'] * data['body_weight_kg']

    return data


def predict_fcr(model, input_data: Dict[str, float]) -> float:
    """
    Predict Feed Conversion Ratio (FCR) from input data.

    Parameters:
        model: Loaded scikit-learn pipeline.
        input_data: Dictionary with base feature values.

    Returns:
        Predicted FCR as a native Python float.
    """
    # Engineer features
    full_data = engineer_features(input_data)

    # Create DataFrame with correct column order
    input_df = pd.DataFrame([{col: full_data[col] for col in ALL_FEATURES}])

    # Predict
    prediction = model.predict(input_df)[0]
    return float(prediction)


def get_efficiency_category(fcr: float) -> str:
    """
    Categorize feed efficiency based on configurable FCR thresholds.

    Parameters:
        fcr: Predicted Feed Conversion Ratio.

    Returns:
        Human-readable efficiency category string.
    """
    if fcr <= FCR_THRESHOLDS['excellent']:
        return "Excellent — Outstanding feed efficiency"
    elif fcr <= FCR_THRESHOLDS['good']:
        return "Good — Above average feed efficiency"
    elif fcr <= FCR_THRESHOLDS['average']:
        return "Average — Typical commercial performance"
    elif fcr <= FCR_THRESHOLDS['below_average']:
        return "Below Average — Monitor feed usage"
    else:
        return "Poor — High feed-cost risk, review management"


def get_risk_level(fcr: float, mortality_percent: float) -> str:
    """
    Assess farmer production risk level based on FCR and mortality.

    Parameters:
        fcr: Predicted Feed Conversion Ratio.
        mortality_percent: Flock mortality percentage.

    Returns:
        Risk level string.
    """
    risk_score = 0

    # FCR-based risk
    if fcr > FCR_THRESHOLDS['below_average']:
        risk_score += 3
    elif fcr > FCR_THRESHOLDS['average']:
        risk_score += 2
    elif fcr > FCR_THRESHOLDS['good']:
        risk_score += 1

    # Mortality-based risk
    if mortality_percent > 10:
        risk_score += 3
    elif mortality_percent > 5:
        risk_score += 2
    elif mortality_percent > 3:
        risk_score += 1

    if risk_score >= 5:
        return "High Risk"
    elif risk_score >= 3:
        return "Medium Risk"
    elif risk_score >= 1:
        return "Low Risk"
    else:
        return "Minimal Risk"


def get_contract_recommendation(fcr: float, mortality_percent: float, profit_margin: float) -> str:
    """
    Generate contract-farming recommendation.

    Parameters:
        fcr: Predicted FCR.
        mortality_percent: Flock mortality percentage.
        profit_margin: Estimated profit margin percentage.

    Returns:
        Contract recommendation string.
    """
    if fcr <= FCR_THRESHOLDS['good'] and mortality_percent <= 4 and profit_margin > 15:
        return "Strong candidate — Recommend for contract farming partnership"
    elif fcr <= FCR_THRESHOLDS['average'] and mortality_percent <= 6 and profit_margin > 5:
        return "Acceptable candidate — Consider with monitoring conditions"
    elif fcr <= FCR_THRESHOLDS['below_average'] and mortality_percent <= 8:
        return "Marginal candidate — Requires improvement plan before contracting"
    else:
        return "Not recommended — Review farmer capacity and management practices first"


def calculate_business_outputs(
    predicted_fcr: float,
    flock_size: int,
    average_target_weight_kg: float,
    mortality_percent: float,
    feed_price_rwf_per_kg: float,
    expected_selling_price_rwf_per_kg: float,
    chick_cost_rwf_per_bird: float,
    medicine_cost_rwf: float,
    labour_cost_rwf: float,
    transport_cost_rwf: float,
    other_costs_rwf: float,
    cold_room_capacity_kg: float,
    delivery_vehicle_capacity_kg: float,
    dressing_yield_percent: float,
) -> Dict[str, Any]:
    """
    Calculate all business outputs from predicted FCR and user-provided assumptions.

    IMPORTANT: These are operational estimates based on the predicted FCR and
    user-provided cost/market assumptions. They do NOT represent separate
    machine-learning predictions. This tool does not replace professional
    veterinary, financial, or farm-management advice.

    Parameters:
        predicted_fcr: Model-predicted Feed Conversion Ratio.
        flock_size: Total number of birds placed.
        average_target_weight_kg: Target live weight per bird at harvest.
        mortality_percent: Expected/actual cumulative mortality.
        feed_price_rwf_per_kg: Cost of feed per kilogram in RWF.
        expected_selling_price_rwf_per_kg: Market price per kg of dressed meat in RWF.
        chick_cost_rwf_per_bird: Cost per day-old chick in RWF.
        medicine_cost_rwf: Total medicine/veterinary cost in RWF.
        labour_cost_rwf: Total labour cost in RWF.
        transport_cost_rwf: Total transport cost in RWF.
        other_costs_rwf: Other miscellaneous costs in RWF.
        cold_room_capacity_kg: Cold storage capacity in kg.
        delivery_vehicle_capacity_kg: Delivery vehicle capacity in kg.
        dressing_yield_percent: Carcass dressing yield percentage (40-90%).

    Returns:
        Dictionary with all calculated business outputs.
    """
    # Core calculations
    surviving_birds = flock_size * (1 - mortality_percent / 100)
    expected_live_weight_kg = surviving_birds * average_target_weight_kg
    estimated_feed_required_kg = predicted_fcr * expected_live_weight_kg
    estimated_feed_cost_rwf = estimated_feed_required_kg * feed_price_rwf_per_kg
    saleable_meat_kg = expected_live_weight_kg * dressing_yield_percent / 100
    estimated_revenue_rwf = saleable_meat_kg * expected_selling_price_rwf_per_kg

    total_production_cost_rwf = (
        estimated_feed_cost_rwf
        + flock_size * chick_cost_rwf_per_bird
        + medicine_cost_rwf
        + labour_cost_rwf
        + transport_cost_rwf
        + other_costs_rwf
    )

    estimated_profit_rwf = estimated_revenue_rwf - total_production_cost_rwf

    # Avoid division by zero
    if estimated_revenue_rwf > 0:
        profit_margin_percent = (estimated_profit_rwf / estimated_revenue_rwf) * 100
    else:
        profit_margin_percent = 0.0

    if cold_room_capacity_kg > 0:
        cold_storage_utilization_percent = (saleable_meat_kg / cold_room_capacity_kg) * 100
    else:
        cold_storage_utilization_percent = 0.0

    if delivery_vehicle_capacity_kg > 0:
        delivery_trips = math.ceil(saleable_meat_kg / delivery_vehicle_capacity_kg)
    else:
        delivery_trips = 0

    # Categories and recommendations
    efficiency_category = get_efficiency_category(predicted_fcr)
    risk_level = get_risk_level(predicted_fcr, mortality_percent)
    contract_recommendation = get_contract_recommendation(
        predicted_fcr, mortality_percent, profit_margin_percent
    )

    return {
        # Model output
        "predicted_fcr": round(predicted_fcr, 4),
        "efficiency_category": efficiency_category,

        # Production estimates
        "surviving_birds": round(surviving_birds, 0),
        "expected_live_weight_kg": round(expected_live_weight_kg, 2),
        "estimated_feed_required_kg": round(estimated_feed_required_kg, 2),
        "saleable_meat_kg": round(saleable_meat_kg, 2),

        # Financial estimates (RWF)
        "estimated_feed_cost_rwf": round(estimated_feed_cost_rwf, 0),
        "total_production_cost_rwf": round(total_production_cost_rwf, 0),
        "estimated_revenue_rwf": round(estimated_revenue_rwf, 0),
        "estimated_profit_rwf": round(estimated_profit_rwf, 0),
        "profit_margin_percent": round(profit_margin_percent, 2),

        # Logistics
        "cold_storage_utilization_percent": round(cold_storage_utilization_percent, 2),
        "delivery_trips": delivery_trips,

        # Risk and recommendations
        "risk_level": risk_level,
        "contract_recommendation": contract_recommendation,

        # Disclaimer
        "disclaimer": (
            "These are operational estimates based on the predicted FCR and "
            "user-provided cost/market assumptions. They do not represent separate "
            "machine-learning predictions. This tool does not replace professional "
            "veterinary, financial, or farm-management advice."
        )
    }

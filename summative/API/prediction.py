"""
Earthwise AI Poultry Production and Feed Efficiency Advisor — FastAPI Backend
=============================================================================
API for predicting broiler Feed Conversion Ratio (FCR) and deriving
business insights for poultry value chains.

Endpoints:
    GET  /           — API info and status
    GET  /health     — Model health check
    POST /predict    — FCR prediction + business calculations
    POST /retrain    — Model retraining from uploaded CSV
    GET  /model-info — Model metadata and metrics
"""

import os
import io
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model_service import (
    load_model, load_metadata, predict_fcr, calculate_business_outputs
)
from retrain import validate_uploaded_data, retrain_models

# ============================================================
# Logging Configuration
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# FastAPI Application
# ============================================================
app = FastAPI(
    title="Earthwise AI Poultry FCR Advisor",
    description=(
        "Predicts broiler Feed Conversion Ratio (FCR) and derives business "
        "insights for poultry production, cold-chain operations, and farmer "
        "assessment. Part of the Earthwise poultry value chain platform."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================
# CORS Configuration
# ============================================================
# CORS origins are restricted to reduce unauthorized browser-based access.
# Flutter mobile applications usually do not rely on browser CORS enforcement,
# but Swagger UI and any browser-based clients do.
# Production origins should be set through the ALLOWED_ORIGINS environment variable.
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost,http://localhost:3000,http://127.0.0.1,http://10.0.2.2"
).split(",")

app.add_middleware(
    CORSMiddleware,
    # Do NOT use allow_origins=["*"] — restrict to known origins
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    # Credentials disabled because no authentication cookies are used
    allow_credentials=False,
    # Only the HTTP methods actually needed by our endpoints
    allow_methods=["GET", "POST", "OPTIONS"],
    # Only the headers our clients send
    allow_headers=["Content-Type", "Authorization"],
)

# ============================================================
# Load Model on Startup
# ============================================================
model = None
metadata = None

@app.on_event("startup")
async def startup_event():
    """Load model and metadata when the API starts."""
    global model, metadata
    try:
        model = load_model()
        metadata = load_metadata()
        logger.info(f"Model loaded: {metadata.get('model_name', 'unknown')} "
                     f"v{metadata.get('model_version', 'unknown')}")
    except FileNotFoundError as e:
        logger.error(f"Model loading failed: {e}")
        logger.warning("API starting without a model. Train the model first.")


# ============================================================
# Pydantic Models
# ============================================================
class PredictionRequest(BaseModel):
    """
    Input data for FCR prediction and business calculations.

    Model Features (used for FCR prediction):
        - age_days, body_weight_kg, harvest_percent, mortality_percent

    Business Inputs (used for financial and logistics calculations):
        - All other fields below
    """
    # --- Model Features ---
    age_days: float = Field(
        ..., ge=20, le=45, description="Age of birds at harvest (days)",
        examples=[27.0]
    )
    body_weight_kg: float = Field(
        ..., ge=0.5, le=3.0, description="Average live body weight at harvest (kg)",
        examples=[1.25]
    )
    harvest_percent: float = Field(
        ..., ge=1.0, le=100.0, description="Percentage of placed birds harvested (%)",
        examples=[40.0]
    )
    mortality_percent: float = Field(
        ..., ge=0.0, le=50.0, description="Cumulative flock mortality (%)",
        examples=[3.5]
    )

    # --- Business Inputs ---
    flock_size: int = Field(
        ..., ge=1, le=1000000, description="Total number of birds placed",
        examples=[5000]
    )
    average_target_weight_kg: float = Field(
        ..., ge=0.5, le=5.0, description="Target live weight per bird at market (kg)",
        examples=[2.0]
    )
    feed_price_rwf_per_kg: float = Field(
        ..., ge=1, le=10000, description="Cost of feed per kilogram (RWF)",
        examples=[450]
    )
    expected_selling_price_rwf_per_kg: float = Field(
        ..., ge=1, le=50000, description="Market price per kg of dressed meat (RWF)",
        examples=[3500]
    )
    chick_cost_rwf_per_bird: float = Field(
        ..., ge=0, le=50000, description="Cost per day-old chick (RWF)",
        examples=[650]
    )
    medicine_cost_rwf: float = Field(
        ..., ge=0, le=100000000, description="Total medicine/veterinary cost (RWF)",
        examples=[250000]
    )
    labour_cost_rwf: float = Field(
        ..., ge=0, le=100000000, description="Total labour cost (RWF)",
        examples=[500000]
    )
    transport_cost_rwf: float = Field(
        ..., ge=0, le=100000000, description="Total transport cost (RWF)",
        examples=[150000]
    )
    other_costs_rwf: float = Field(
        ..., ge=0, le=100000000, description="Other miscellaneous costs (RWF)",
        examples=[100000]
    )
    cold_room_capacity_kg: float = Field(
        ..., ge=1, le=1000000, description="Cold storage capacity (kg)",
        examples=[5000]
    )
    delivery_vehicle_capacity_kg: float = Field(
        ..., ge=1, le=100000, description="Delivery vehicle capacity (kg)",
        examples=[2000]
    )
    dressing_yield_percent: float = Field(
        ..., ge=40, le=90, description="Carcass dressing yield (%)",
        examples=[72]
    )


# ============================================================
# Endpoints
# ============================================================

@app.get("/")
async def root():
    """API information and status."""
    version = metadata.get('model_version', 'unknown') if metadata else 'no model loaded'
    return {
        "api_name": "Earthwise AI Poultry FCR Advisor",
        "status": "operational" if model is not None else "no model loaded",
        "model_version": version,
        "description": (
            "Predicts broiler Feed Conversion Ratio and derives business "
            "insights for poultry value chains."
        ),
        "endpoints": {
            "/docs": "Swagger UI documentation",
            "/health": "Model health check",
            "/predict": "FCR prediction (POST)",
            "/retrain": "Model retraining (POST)",
            "/model-info": "Model metadata"
        }
    }


@app.get("/health")
async def health_check():
    """Confirm that the model is loaded and ready for predictions."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first."
        )
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_name": metadata.get('model_name', 'unknown'),
        "model_version": metadata.get('model_version', 'unknown'),
    }


@app.post("/predict")
async def predict(request: PredictionRequest):
    """
    Predict Feed Conversion Ratio (FCR) and calculate business outputs.

    The ML model predicts only FCR. All other outputs (production estimates,
    financial projections, logistics, risk level, contract recommendation)
    are calculated using transparent business rules and user-provided assumptions.
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first."
        )

    try:
        # Extract model features
        model_input = {
            'age_days': request.age_days,
            'body_weight_kg': request.body_weight_kg,
            'harvest_percent': request.harvest_percent,
            'mortality_percent': request.mortality_percent,
        }

        # Predict FCR
        predicted_fcr = predict_fcr(model, model_input)

        # Calculate business outputs
        business_outputs = calculate_business_outputs(
            predicted_fcr=predicted_fcr,
            flock_size=request.flock_size,
            average_target_weight_kg=request.average_target_weight_kg,
            mortality_percent=request.mortality_percent,
            feed_price_rwf_per_kg=request.feed_price_rwf_per_kg,
            expected_selling_price_rwf_per_kg=request.expected_selling_price_rwf_per_kg,
            chick_cost_rwf_per_bird=request.chick_cost_rwf_per_bird,
            medicine_cost_rwf=request.medicine_cost_rwf,
            labour_cost_rwf=request.labour_cost_rwf,
            transport_cost_rwf=request.transport_cost_rwf,
            other_costs_rwf=request.other_costs_rwf,
            cold_room_capacity_kg=request.cold_room_capacity_kg,
            delivery_vehicle_capacity_kg=request.delivery_vehicle_capacity_kg,
            dressing_yield_percent=request.dressing_yield_percent,
        )

        return business_outputs

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/retrain")
async def retrain_endpoint(file: UploadFile = File(...)):
    """
    Retrain the model with new data.

    Upload a CSV file with columns: age_days, body_weight_kg, harvest_percent,
    mortality_percent, and either 'fcr' or 'production_index' (IP).

    The endpoint will:
    1. Validate the uploaded data
    2. Backup the current model
    3. Retrain all candidate models (Linear Regression, SGD, Decision Tree, Random Forest)
    4. Select the best model by test RMSE
    5. Replace the deployed model only if the new model passes checks
    6. Return before/after metrics

    WARNING: In production, this endpoint MUST require authentication and rate limiting.
    """
    global model, metadata

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file.")

    try:
        # Read uploaded file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        logger.info(f"Received retraining data: {df.shape[0]} rows, {df.shape[1]} columns")

        # Validate data
        df_clean, warnings = validate_uploaded_data(df)
        logger.info(f"Data validated: {df_clean.shape[0]} clean rows")

        # Retrain models
        result = retrain_models(df_clean)

        # Reload model
        model = load_model()
        metadata = load_metadata()

        result['data_warnings'] = warnings
        return result

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Retraining error: {e}")
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")


@app.get("/model-info")
async def model_info():
    """Return model metadata, feature list, target, version, and evaluation metrics."""
    if metadata is None:
        raise HTTPException(
            status_code=503,
            detail="Model metadata not available. Please train the model first."
        )
    return {
        "model_name": metadata.get('model_name'),
        "model_version": metadata.get('model_version'),
        "target": metadata.get('target'),
        "features": metadata.get('features'),
        "base_features": metadata.get('base_features'),
        "engineered_features": metadata.get('engineered_features'),
        "training_date": metadata.get('training_date'),
        "training_samples": metadata.get('training_samples'),
        "test_samples": metadata.get('test_samples'),
        "metrics": metadata.get('metrics'),
        "all_model_results": metadata.get('all_model_results'),
    }


# ============================================================
# Run with: uvicorn prediction:app --reload
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("prediction:app", host="0.0.0.0", port=8000, reload=True)

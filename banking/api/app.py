"""
REST API for Banking Churn Prediction
FastAPI-based prediction service
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from banking.scripts.monitoring import ModelPerformanceMonitor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Banking Churn Prediction API",
    description="ML-powered customer churn prediction service",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
model_data = None
monitor = ModelPerformanceMonitor()


@app.on_event("startup")
async def load_model():
    """Load ML model on application startup"""
    global model_data
    try:
        model_path = os.path.join(
            os.path.dirname(__file__), "../models/churn_model.pkl"
        )
        model_data = joblib.load(model_path)
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise


# Request/Response Models
class CustomerData(BaseModel):
    """Customer data for prediction"""

    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    age: int = Field(..., ge=18, le=100, description="Customer age")
    tenure: int = Field(..., ge=0, le=20, description="Years with bank")
    balance: float = Field(..., ge=0, description="Account balance")
    products_number: int = Field(..., ge=1, le=5, description="Number of products")
    credit_card: int = Field(..., ge=0, le=1, description="Has credit card (0/1)")
    active_member: int = Field(..., ge=0, le=1, description="Is active member (0/1)")
    estimated_salary: float = Field(..., ge=0, description="Estimated annual salary")
    txn_count: int = Field(..., ge=0, description="Transaction count")
    days_since_last_txn: int = Field(
        ..., ge=0, description="Days since last transaction"
    )
    country: str = Field(..., description="Country")
    gender: str = Field(..., description="Gender")

    @validator("country")
    def validate_country(cls, v):
        allowed = ["Germany", "France", "Spain", "United States", "United Kingdom"]
        if v not in allowed:
            raise ValueError(f"Country must be one of: {allowed}")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        if v not in ["Male", "Female"]:
            raise ValueError("Gender must be 'Male' or 'Female'")
        return v

    class Config:
        schema_extra = {
            "example": {
                "credit_score": 650,
                "age": 35,
                "tenure": 5,
                "balance": 50000.0,
                "products_number": 2,
                "credit_card": 1,
                "active_member": 1,
                "estimated_salary": 75000.0,
                "txn_count": 25,
                "days_since_last_txn": 30,
                "country": "United States",
                "gender": "Male",
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response"""

    customer_id: Optional[str] = None
    churn_probability: float = Field(..., description="Probability of churn (0-1)")
    churn_prediction: bool = Field(..., description="Binary churn prediction")
    risk_level: str = Field(..., description="Risk level: Low/Medium/High")
    confidence: str = Field(..., description="Prediction confidence")
    recommendation: str = Field(..., description="Recommended action")
    inference_time_ms: float = Field(..., description="Prediction time in milliseconds")
    timestamp: str = Field(..., description="Prediction timestamp")


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""

    customers: List[CustomerData]


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""

    predictions: List[PredictionResponse]
    total_customers: int
    high_risk_count: int
    total_time_ms: float


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    model_loaded: bool
    timestamp: str
    version: str


# API Endpoints


@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "Banking Churn Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model_data is not None else "unhealthy",
        model_loaded=model_data is not None,
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_churn(customer: CustomerData):
    """
    Predict churn probability for a single customer

    Args:
        customer: Customer data

    Returns:
        Prediction with probability and risk level
    """
    if model_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_time = time.time()

    try:
        # Prepare data
        customer_dict = customer.dict()
        customer_df = pd.DataFrame([customer_dict])

        # Encode categorical variables
        customer_df["country_encoded"] = model_data["label_encoders"][
            "country"
        ].transform([customer_dict["country"]])[0]
        customer_df["gender_encoded"] = model_data["label_encoders"][
            "gender"
        ].transform([customer_dict["gender"]])[0]

        # Select features and scale
        X_new = customer_df[model_data["features"]]
        X_new_scaled = model_data["scaler"].transform(X_new)

        # Predict
        probability = float(model_data["model"].predict_proba(X_new_scaled)[0, 1])
        prediction = bool(probability >= model_data["optimal_threshold"])

        # Calculate inference time
        inference_time = (time.time() - start_time) * 1000

        # Determine risk level
        if probability >= 0.7:
            risk_level = "High"
            confidence = "High"
            recommendation = "Immediate retention actions needed - offer incentives"
        elif probability >= 0.4:
            risk_level = "Medium"
            confidence = "Medium"
            recommendation = "Monitor closely - consider engagement campaign"
        else:
            risk_level = "Low"
            confidence = "High"
            recommendation = "Continue regular monitoring"

        # Track prediction
        monitor.track_predictions(np.array([prediction]), np.array([probability]))

        return PredictionResponse(
            churn_probability=round(probability, 4),
            churn_prediction=prediction,
            risk_level=risk_level,
            confidence=confidence,
            recommendation=recommendation,
            inference_time_ms=round(inference_time, 2),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_churn_batch(request: BatchPredictionRequest):
    """
    Predict churn for multiple customers

    Args:
        request: Batch prediction request with list of customers

    Returns:
        Batch predictions with summary statistics
    """
    if model_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_time = time.time()
    predictions = []
    high_risk_count = 0

    try:
        for customer in request.customers:
            # Reuse single prediction endpoint
            prediction = await predict_churn(customer)
            predictions.append(prediction)

            if prediction.risk_level == "High":
                high_risk_count += 1

        total_time = (time.time() - start_time) * 1000

        return BatchPredictionResponse(
            predictions=predictions,
            total_customers=len(predictions),
            high_risk_count=high_risk_count,
            total_time_ms=round(total_time, 2),
        )

    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Batch prediction failed: {str(e)}"
        )


@app.get("/model/info", tags=["Model"])
async def get_model_info():
    """Get model information and metadata"""
    if model_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_type": type(model_data["model"]).__name__,
        "features": model_data["features"],
        "num_features": len(model_data["features"]),
        "optimal_threshold": float(model_data["optimal_threshold"]),
        "label_encoders": {
            "country": list(model_data["label_encoders"]["country"].classes_),
            "gender": list(model_data["label_encoders"]["gender"].classes_),
        },
    }


@app.get("/model/features", tags=["Model"])
async def get_feature_importance():
    """Get feature importance (if available)"""
    if model_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if hasattr(model_data["model"], "feature_importances_"):
        importance_dict = {
            feature: float(importance)
            for feature, importance in zip(
                model_data["features"], model_data["model"].feature_importances_
            )
        }

        # Sort by importance
        sorted_importance = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        )

        return {
            "feature_importance": sorted_importance,
            "top_5_features": list(sorted_importance.keys())[:5],
        }
    else:
        return {"message": "Feature importance not available for this model type"}


# Run with: uvicorn api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

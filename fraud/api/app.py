"""
REST API for Fraud Detection system.
Provides endpoints for fraud prediction, transaction analysis, and monitoring.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Fraud Detection API",
    description="API for fraud detection and transaction analysis",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


class Transaction(BaseModel):
    """Transaction model for fraud prediction"""

    transaction_id: str
    user_id: str
    amount: float = Field(gt=0, description="Transaction amount")
    merchant: Optional[str] = None
    category: Optional[str] = None


class FraudPrediction(BaseModel):
    """Fraud prediction response"""

    transaction_id: str
    is_fraud: bool
    fraud_probability: float
    risk_level: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fraud Detection API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/transactions",
            "/transactions/{transaction_id}",
            "/predict",
            "/stats",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "fraud-detection",
    }


@app.get("/transactions")
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000), fraud_only: bool = False
):
    """Get transaction data"""
    try:
        # Try to load fraud transactions
        fraud_file = DATA_DIR / "fraud_transactions_clean.csv"

        if not fraud_file.exists():
            raise HTTPException(status_code=404, detail="Transaction data not found")

        df = pd.read_csv(fraud_file)

        if fraud_only:
            fraud_col = next(
                (col for col in df.columns if "fraud" in col.lower()), None
            )
            if fraud_col:
                df = df[df[fraud_col] == 1]

        df = df.head(limit)

        return {"count": len(df), "transactions": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get specific transaction by ID"""
    try:
        fraud_file = DATA_DIR / "fraud_transactions_clean.csv"

        if not fraud_file.exists():
            raise HTTPException(status_code=404, detail="Transaction data not found")

        df = pd.read_csv(fraud_file)

        # Find transaction ID column
        id_col = next(
            (
                col
                for col in df.columns
                if "transaction" in col.lower() and "id" in col.lower()
            ),
            None,
        )

        if not id_col:
            raise HTTPException(
                status_code=500, detail="Transaction ID column not found"
            )

        transaction = df[df[id_col].astype(str) == transaction_id]

        if len(transaction) == 0:
            raise HTTPException(
                status_code=404, detail=f"Transaction {transaction_id} not found"
            )

        return transaction.iloc[0].to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=FraudPrediction)
async def predict_fraud(transaction: Transaction):
    """Predict if a transaction is fraudulent"""
    try:
        # Simple rule-based prediction (replace with actual ML model)
        fraud_score = 0.0

        # High amount = higher risk
        if transaction.amount > 1000:
            fraud_score += 0.3
        if transaction.amount > 5000:
            fraud_score += 0.2

        # Random component (replace with real model)
        fraud_score += np.random.random() * 0.5

        fraud_score = min(fraud_score, 1.0)

        is_fraud = fraud_score > 0.5

        if fraud_score < 0.3:
            risk_level = "Low"
        elif fraud_score < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"

        return FraudPrediction(
            transaction_id=transaction.transaction_id,
            is_fraud=is_fraud,
            fraud_probability=round(fraud_score, 3),
            risk_level=risk_level,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get fraud detection statistics"""
    try:
        fraud_file = DATA_DIR / "fraud_transactions_clean.csv"

        if not fraud_file.exists():
            raise HTTPException(status_code=404, detail="Transaction data not found")

        df = pd.read_csv(fraud_file)

        fraud_col = next((col for col in df.columns if "fraud" in col.lower()), None)
        amount_col = next((col for col in df.columns if "amount" in col.lower()), None)

        stats = {"total_transactions": len(df), "timestamp": datetime.now().isoformat()}

        if fraud_col:
            stats["fraud_count"] = int(df[fraud_col].sum())
            stats["fraud_rate"] = float(df[fraud_col].mean())

        if amount_col:
            stats["total_amount"] = float(df[amount_col].sum())
            stats["avg_amount"] = float(df[amount_col].mean())
            stats["max_amount"] = float(df[amount_col].max())

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

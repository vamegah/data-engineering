"""
REST API for E-commerce Analytics system.
Provides endpoints for customer segmentation, product analysis, and RFM metrics.
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
    title="E-commerce Analytics API",
    description="API for e-commerce customer and product analytics",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


class Customer(BaseModel):
    """Customer model"""

    customer_id: str
    tier: Optional[str] = None
    location: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "E-commerce Analytics API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/customers",
            "/customers/{customer_id}",
            "/products",
            "/segments",
            "/stats",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ecommerce-analytics",
    }


@app.get("/customers")
async def get_customers(
    limit: int = Query(100, ge=1, le=1000), tier: Optional[str] = None
):
    """Get customer data"""
    try:
        customers_file = DATA_DIR / "ecommerce_customers_clean.csv"

        if not customers_file.exists():
            raise HTTPException(status_code=404, detail="Customer data not found")

        df = pd.read_csv(customers_file)

        if tier:
            tier_col = next((col for col in df.columns if "tier" in col.lower()), None)
            if tier_col:
                df = df[df[tier_col] == tier]

        df = df.head(limit)

        return {"count": len(df), "customers": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get specific customer by ID"""
    try:
        customers_file = DATA_DIR / "ecommerce_customers_clean.csv"

        if not customers_file.exists():
            raise HTTPException(status_code=404, detail="Customer data not found")

        df = pd.read_csv(customers_file)

        id_col = next(
            (
                col
                for col in df.columns
                if "customer" in col.lower() and "id" in col.lower()
            ),
            None,
        )

        if not id_col:
            raise HTTPException(status_code=500, detail="Customer ID column not found")

        customer = df[df[id_col].astype(str) == customer_id]

        if len(customer) == 0:
            raise HTTPException(
                status_code=404, detail=f"Customer {customer_id} not found"
            )

        return customer.iloc[0].to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products")
async def get_products(limit: int = Query(100, ge=1, le=1000)):
    """Get product catalog"""
    try:
        products_file = DATA_DIR / "ecommerce_products_clean.csv"

        if not products_file.exists():
            raise HTTPException(status_code=404, detail="Product data not found")

        df = pd.read_csv(products_file)
        df = df.head(limit)

        return {"count": len(df), "products": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/segments")
async def get_customer_segments():
    """Get customer segmentation analysis"""
    try:
        customers_file = DATA_DIR / "ecommerce_customers_clean.csv"

        if not customers_file.exists():
            raise HTTPException(status_code=404, detail="Customer data not found")

        df = pd.read_csv(customers_file)

        tier_col = next((col for col in df.columns if "tier" in col.lower()), None)

        segments = {}

        if tier_col:
            segment_counts = df[tier_col].value_counts().to_dict()
            segments = {"by_tier": segment_counts, "total_customers": len(df)}

        return segments

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get e-commerce statistics"""
    try:
        stats = {"timestamp": datetime.now().isoformat()}

        # Customer stats
        customers_file = DATA_DIR / "ecommerce_customers_clean.csv"
        if customers_file.exists():
            customers = pd.read_csv(customers_file)
            stats["total_customers"] = len(customers)

        # Transaction stats
        txns_file = DATA_DIR / "ecommerce_transactions_clean.csv"
        if txns_file.exists():
            txns = pd.read_csv(txns_file)
            stats["total_transactions"] = len(txns)

            amount_col = next(
                (col for col in txns.columns if "amount" in col.lower()), None
            )
            if amount_col:
                stats["total_revenue"] = float(txns[amount_col].sum())
                stats["avg_order_value"] = float(txns[amount_col].mean())

        # Product stats
        products_file = DATA_DIR / "ecommerce_products_clean.csv"
        if products_file.exists():
            products = pd.read_csv(products_file)
            stats["total_products"] = len(products)

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)

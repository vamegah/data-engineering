"""
REST API for Financial Analytics system.
Provides endpoints for stock analysis, LSTM predictions, and portfolio metrics.
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
    title="Financial Analytics API",
    description="API for stock market analysis and predictions",
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


class StockQuery(BaseModel):
    """Stock query model"""

    ticker: str = Field(description="Stock ticker symbol")
    days: int = Field(default=30, ge=1, le=365, description="Number of days")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial Analytics API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/stocks",
            "/stocks/latest",
            "/predict",
            "/technical-indicators",
            "/stats",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "financial-analytics",
    }


@app.get("/stocks")
async def get_stocks(
    limit: int = Query(100, ge=1, le=1000), ticker: Optional[str] = None
):
    """Get stock price data"""
    try:
        stocks_file = DATA_DIR / "financial_stocks_clean.csv"

        if not stocks_file.exists():
            raise HTTPException(status_code=404, detail="Stock data not found")

        df = pd.read_csv(stocks_file)

        if ticker:
            ticker_col = next(
                (
                    col
                    for col in df.columns
                    if "ticker" in col.lower() or "symbol" in col.lower()
                ),
                None,
            )
            if ticker_col:
                df = df[df[ticker_col] == ticker.upper()]

        df = df.head(limit)

        return {"count": len(df), "stocks": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stocks/latest")
async def get_latest_prices():
    """Get latest stock prices"""
    try:
        stocks_file = DATA_DIR / "financial_stocks_clean.csv"

        if not stocks_file.exists():
            raise HTTPException(status_code=404, detail="Stock data not found")

        df = pd.read_csv(stocks_file)

        # Get date column
        date_col = next((col for col in df.columns if "date" in col.lower()), None)

        if date_col:
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col, ascending=False)

            # Get most recent date
            latest_date = df[date_col].max()
            latest_data = df[df[date_col] == latest_date]

            return {
                "date": latest_date.isoformat(),
                "count": len(latest_data),
                "prices": latest_data.to_dict(orient="records"),
            }

        return {"stocks": df.head(10).to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
async def predict_price(query: StockQuery):
    """Predict future stock price using LSTM model"""
    try:
        # Placeholder for LSTM model prediction
        # In production, load actual model and make predictions

        current_price = 100 + np.random.random() * 50
        predicted_price = current_price * (1 + (np.random.random() - 0.5) * 0.1)

        return {
            "ticker": query.ticker,
            "prediction_days": query.days,
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "change_percent": round(
                (predicted_price - current_price) / current_price * 100, 2
            ),
            "model": "LSTM",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/technical-indicators")
async def get_technical_indicators(ticker: Optional[str] = None):
    """Get technical indicators for stocks"""
    try:
        stocks_file = DATA_DIR / "financial_stocks_clean.csv"

        if not stocks_file.exists():
            raise HTTPException(status_code=404, detail="Stock data not found")

        df = pd.read_csv(stocks_file)

        if ticker:
            ticker_col = next(
                (col for col in df.columns if "ticker" in col.lower()), None
            )
            if ticker_col:
                df = df[df[ticker_col] == ticker.upper()]

        close_col = next(
            (col for col in df.columns if col.lower() in ["close", "closing_price"]),
            None,
        )

        indicators = {}

        if close_col and len(df) > 0:
            # Calculate simple indicators
            indicators = {
                "current_price": float(df[close_col].iloc[-1]),
                "sma_20": (
                    float(df[close_col].rolling(20).mean().iloc[-1])
                    if len(df) >= 20
                    else None
                ),
                "sma_50": (
                    float(df[close_col].rolling(50).mean().iloc[-1])
                    if len(df) >= 50
                    else None
                ),
                "volatility": float(df[close_col].std()),
                "min_price": float(df[close_col].min()),
                "max_price": float(df[close_col].max()),
            }

        return indicators

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get financial market statistics"""
    try:
        stocks_file = DATA_DIR / "financial_stocks_clean.csv"

        if not stocks_file.exists():
            raise HTTPException(status_code=404, detail="Stock data not found")

        df = pd.read_csv(stocks_file)

        stats = {"total_records": len(df), "timestamp": datetime.now().isoformat()}

        close_col = next(
            (col for col in df.columns if col.lower() in ["close", "closing_price"]),
            None,
        )

        if close_col:
            stats["avg_price"] = float(df[close_col].mean())
            stats["median_price"] = float(df[close_col].median())
            stats["price_range"] = {
                "min": float(df[close_col].min()),
                "max": float(df[close_col].max()),
            }

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
REST API for HR Analytics system.
Provides endpoints for attrition prediction, employee risk analysis, and sentiment insights.
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
    title="HR Analytics API",
    description="API for employee attrition prediction and HR analytics",
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

# Privacy settings
ANONYMIZE_DATA = os.getenv("ANONYMIZE_EMPLOYEE_DATA", "true").lower() == "true"


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HR Analytics API",
        "version": "1.0.0",
        "data_anonymized": ANONYMIZE_DATA,
        "endpoints": [
            "/health",
            "/employees",
            "/employees/risk",
            "/exit-interviews",
            "/sentiment",
            "/stats",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "hr-analytics",
        "data_anonymized": ANONYMIZE_DATA,
    }


@app.get("/employees")
async def get_employees(
    limit: int = Query(100, ge=1, le=1000), department: Optional[str] = None
):
    """Get employee data (anonymized)"""
    try:
        employees_file = DATA_DIR / "employees_clean.csv"

        if not employees_file.exists():
            raise HTTPException(status_code=404, detail="Employee data not found")

        df = pd.read_csv(employees_file)

        if department:
            dept_col = next(
                (col for col in df.columns if "department" in col.lower()), None
            )
            if dept_col:
                df = df[df[dept_col].str.lower() == department.lower()]

        df = df.head(limit)

        # Remove PII if anonymization is enabled
        if ANONYMIZE_DATA:
            pii_keywords = ["name", "email", "phone", "address", "ssn"]
            cols_to_drop = [
                col for col in df.columns if any(k in col.lower() for k in pii_keywords)
            ]
            df = df.drop(columns=cols_to_drop, errors="ignore")

        return {
            "count": len(df),
            "employees": df.to_dict(orient="records"),
            "data_anonymized": ANONYMIZE_DATA,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/employees/risk")
async def get_employee_risk(
    limit: int = Query(100, ge=1, le=1000), high_risk_only: bool = False
):
    """Get employee attrition risk scores"""
    try:
        risk_file = DATA_DIR / "employee_risk_scores.csv"

        if not risk_file.exists():
            raise HTTPException(status_code=404, detail="Risk score data not found")

        df = pd.read_csv(risk_file)

        if high_risk_only:
            risk_col = next(
                (
                    col
                    for col in df.columns
                    if "risk" in col.lower() or "score" in col.lower()
                ),
                None,
            )
            if risk_col:
                df = df[df[risk_col] > 0.5]

        df = df.head(limit)

        # Remove PII
        if ANONYMIZE_DATA:
            pii_keywords = ["name", "email", "phone", "ssn"]
            cols_to_drop = [
                col for col in df.columns if any(k in col.lower() for k in pii_keywords)
            ]
            df = df.drop(columns=cols_to_drop, errors="ignore")

        return {"count": len(df), "risk_scores": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exit-interviews")
async def get_exit_interviews(limit: int = Query(100, ge=1, le=1000)):
    """Get exit interview data"""
    try:
        exit_file = DATA_DIR / "exit_interviews_clean.csv"

        if not exit_file.exists():
            raise HTTPException(status_code=404, detail="Exit interview data not found")

        df = pd.read_csv(exit_file)
        df = df.head(limit)

        # Remove PII
        if ANONYMIZE_DATA:
            pii_keywords = ["name", "email", "phone"]
            cols_to_drop = [
                col for col in df.columns if any(k in col.lower() for k in pii_keywords)
            ]
            df = df.drop(columns=cols_to_drop, errors="ignore")

        return {"count": len(df), "interviews": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sentiment")
async def get_sentiment_analysis():
    """Get exit interview sentiment analysis"""
    try:
        sentiment_file = DATA_DIR / "sentiment_analysis_results.csv"

        if not sentiment_file.exists():
            raise HTTPException(status_code=404, detail="Sentiment data not found")

        df = pd.read_csv(sentiment_file)

        return {"count": len(df), "sentiment": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get HR statistics"""
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "data_anonymized": ANONYMIZE_DATA,
        }

        # Employee stats
        employees_file = DATA_DIR / "employees_clean.csv"
        if employees_file.exists():
            employees = pd.read_csv(employees_file)
            stats["total_employees"] = len(employees)

            attrition_col = next(
                (col for col in employees.columns if "attrition" in col.lower()), None
            )
            if attrition_col:
                stats["attrition_rate"] = float(employees[attrition_col].mean())

        # Risk scores
        risk_file = DATA_DIR / "employee_risk_scores.csv"
        if risk_file.exists():
            risk = pd.read_csv(risk_file)
            risk_col = next(
                (
                    col
                    for col in risk.columns
                    if "risk" in col.lower() or "score" in col.lower()
                ),
                None,
            )
            if risk_col:
                stats["high_risk_employees"] = int((risk[risk_col] > 0.5).sum())
                stats["avg_risk_score"] = float(risk[risk_col].mean())

        # Exit interviews
        exit_file = DATA_DIR / "exit_interviews_clean.csv"
        if exit_file.exists():
            exit_data = pd.read_csv(exit_file)
            stats["total_exit_interviews"] = len(exit_data)

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)

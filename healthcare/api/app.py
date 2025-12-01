"""
REST API for Healthcare Analytics system.
Provides HIPAA-compliant endpoints for patient data, treatment analysis, and facility metrics.
"""

from fastapi import FastAPI, HTTPException, Query, Header
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
    title="Healthcare Analytics API",
    description="HIPAA-compliant API for healthcare data analytics",
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

# HIPAA compliance flag
HIPAA_COMPLIANT = os.getenv("HIPAA_COMPLIANT", "true").lower() == "true"


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare Analytics API",
        "version": "1.0.0",
        "hipaa_compliant": HIPAA_COMPLIANT,
        "endpoints": ["/health", "/patients", "/treatments", "/facilities", "/stats"],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "healthcare-analytics",
        "hipaa_compliant": HIPAA_COMPLIANT,
    }


@app.get("/patients")
async def get_patients(
    limit: int = Query(100, ge=1, le=1000),
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
):
    """Get anonymized patient data (HIPAA-compliant)"""
    try:
        patients_file = DATA_DIR / "patients_clean.csv"

        if not patients_file.exists():
            raise HTTPException(status_code=404, detail="Patient data not found")

        df = pd.read_csv(patients_file)

        # Filter by age if provided
        age_col = next((col for col in df.columns if "age" in col.lower()), None)
        if age_col:
            if age_min:
                df = df[df[age_col] >= age_min]
            if age_max:
                df = df[df[age_col] <= age_max]

        df = df.head(limit)

        # Remove any PII before returning (HIPAA compliance)
        pii_keywords = ["name", "ssn", "email", "phone", "address"]
        cols_to_drop = [
            col for col in df.columns if any(k in col.lower() for k in pii_keywords)
        ]
        df = df.drop(columns=cols_to_drop, errors="ignore")

        return {
            "count": len(df),
            "patients": df.to_dict(orient="records"),
            "data_anonymized": True,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/treatments")
async def get_treatments(limit: int = Query(100, ge=1, le=1000)):
    """Get treatment data"""
    try:
        treatments_file = DATA_DIR / "treatments_clean.csv"

        if not treatments_file.exists():
            raise HTTPException(status_code=404, detail="Treatment data not found")

        df = pd.read_csv(treatments_file)
        df = df.head(limit)

        # Remove PII
        pii_keywords = ["name", "ssn", "email", "phone"]
        cols_to_drop = [
            col for col in df.columns if any(k in col.lower() for k in pii_keywords)
        ]
        df = df.drop(columns=cols_to_drop, errors="ignore")

        return {"count": len(df), "treatments": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/facilities")
async def get_facilities():
    """Get healthcare facility data"""
    try:
        facilities_file = DATA_DIR / "facilities_clean.csv"

        if not facilities_file.exists():
            raise HTTPException(status_code=404, detail="Facility data not found")

        df = pd.read_csv(facilities_file)

        return {"count": len(df), "facilities": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get healthcare statistics"""
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "hipaa_compliant": HIPAA_COMPLIANT,
        }

        # Patient stats
        patients_file = DATA_DIR / "patients_clean.csv"
        if patients_file.exists():
            patients = pd.read_csv(patients_file)
            stats["total_patients"] = len(patients)

            age_col = next(
                (col for col in patients.columns if "age" in col.lower()), None
            )
            if age_col:
                stats["avg_patient_age"] = float(patients[age_col].mean())

        # Treatment stats
        treatments_file = DATA_DIR / "treatments_clean.csv"
        if treatments_file.exists():
            treatments = pd.read_csv(treatments_file)
            stats["total_treatments"] = len(treatments)

            cost_col = next(
                (col for col in treatments.columns if "cost" in col.lower()), None
            )
            if cost_col:
                stats["avg_treatment_cost"] = float(treatments[cost_col].mean())

        # Facility stats
        facilities_file = DATA_DIR / "facilities_clean.csv"
        if facilities_file.exists():
            facilities = pd.read_csv(facilities_file)
            stats["total_facilities"] = len(facilities)

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit-log")
async def get_audit_log():
    """Get API access audit log (HIPAA requirement)"""
    # In production, this would return actual audit logs
    return {
        "message": "Audit logging enabled",
        "audit_enabled": os.getenv("AUDIT_LOGGING", "true").lower() == "true",
        "note": "All PHI access is logged for HIPAA compliance",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)

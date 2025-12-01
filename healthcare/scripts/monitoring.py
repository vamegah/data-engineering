"""
Production monitoring framework for Healthcare Analytics project.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np
import psutil


class HealthcareMonitor:
    """Monitor healthcare analytics system with HIPAA compliance."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            filename=self.log_dir / "healthcare_monitoring.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def check_patient_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check patient data quality (de-identified)."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(data),
            "missing_values_count": int(data.isnull().sum().sum()),
            "duplicate_records": int(data.duplicated().sum()),
        }

        # Check for PHI leakage (should not exist in production)
        phi_columns = ["ssn", "email", "phone", "address"]
        phi_found = [col for col in phi_columns if col in data.columns]
        if phi_found:
            self.logger.error(f"PHI columns detected: {phi_found} - HIPAA VIOLATION")
            metrics["hipaa_alert"] = f"PHI columns found: {phi_found}"

        return metrics

    def track_readmission_predictions(
        self, predictions: np.ndarray, risk_scores: np.ndarray
    ) -> Dict[str, Any]:
        """Track readmission risk predictions."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(predictions),
            "high_risk_patients": int((risk_scores > 0.7).sum()),
            "medium_risk_patients": int(
                ((risk_scores > 0.4) & (risk_scores <= 0.7)).sum()
            ),
            "low_risk_patients": int((risk_scores <= 0.4).sum()),
            "avg_risk_score": float(risk_scores.mean()),
        }

        if metrics["high_risk_patients"] > 50:
            self.logger.warning(
                f"{metrics['high_risk_patients']} high-risk patients identified"
            )

        return metrics

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
        }

    def health_check(self) -> Dict[str, str]:
        """System health check."""
        health = {"status": "healthy", "issues": []}

        if psutil.cpu_percent() > 80:
            health["issues"].append("High CPU usage")
            health["status"] = "warning"

        return health

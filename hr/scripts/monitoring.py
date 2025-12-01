"""
Production monitoring framework for HR Analytics project.
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


class HRMonitor:
    """Monitor HR analytics system."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            filename=self.log_dir / "hr_monitoring.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def check_employee_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check employee data quality."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_employees": len(data),
            "missing_values": data.isnull().sum().to_dict(),
            "duplicate_records": int(data.duplicated().sum()),
        }

        # Check for PII that should be anonymized
        pii_columns = ["ssn", "email", "phone", "address"]
        pii_found = [col for col in pii_columns if col in data.columns]
        if pii_found:
            self.logger.warning(
                f"PII columns detected: {pii_found} - Consider anonymization"
            )

        return metrics

    def track_attrition_predictions(
        self, predictions: np.ndarray, probabilities: np.ndarray
    ) -> Dict[str, Any]:
        """Track attrition prediction metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(predictions),
            "at_risk_employees": int(predictions.sum()),
            "attrition_rate": float(predictions.mean()),
            "avg_risk_score": float(probabilities.mean()),
            "high_risk_employees": int((probabilities > 0.7).sum()),
        }

        if metrics["attrition_rate"] > 0.2:
            self.logger.warning(
                f"High attrition risk detected: {metrics['attrition_rate']:.2%}"
            )

        if metrics["high_risk_employees"] > 10:
            self.logger.warning(
                f"{metrics['high_risk_employees']} high-risk employees identified"
            )

        return metrics

    def analyze_sentiment(self, sentiments: pd.Series) -> Dict[str, Any]:
        """Analyze exit interview sentiment."""
        sentiment_counts = sentiments.value_counts().to_dict()

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_reviews": len(sentiments),
            "sentiment_distribution": sentiment_counts,
            "negative_rate": (
                float((sentiments == "negative").mean())
                if "negative" in sentiment_counts
                else 0.0
            ),
        }

        if metrics["negative_rate"] > 0.5:
            self.logger.warning(
                f"High negative sentiment rate: {metrics['negative_rate']:.2%}"
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

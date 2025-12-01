"""
Production monitoring framework for Fraud Detection project.
Tracks data quality, model performance, and system metrics.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import psutil


class FraudMonitor:
    """Monitor fraud detection system performance."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            filename=self.log_dir / "fraud_monitoring.log",
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def check_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check data quality metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(data),
            "missing_values": data.isnull().sum().to_dict(),
            "duplicate_records": data.duplicated().sum(),
            "data_types": data.dtypes.astype(str).to_dict(),
        }

        # Check for anomalies
        if "amount" in data.columns:
            metrics["amount_stats"] = {
                "mean": float(data["amount"].mean()),
                "std": float(data["amount"].std()),
                "min": float(data["amount"].min()),
                "max": float(data["amount"].max()),
            }

        # Alert if issues found
        if metrics["duplicate_records"] > 0:
            self.logger.warning(
                f"Found {metrics['duplicate_records']} duplicate records"
            )

        if data.isnull().sum().sum() > 0:
            self.logger.warning(
                f"Found missing values: {data.isnull().sum().to_dict()}"
            )

        return metrics

    def track_predictions(
        self, predictions: np.ndarray, probabilities: np.ndarray
    ) -> Dict[str, Any]:
        """Track fraud prediction metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(predictions),
            "fraud_detected": int(predictions.sum()),
            "fraud_rate": float(predictions.mean()),
            "avg_fraud_probability": float(probabilities.mean()),
            "max_fraud_probability": float(probabilities.max()),
            "high_risk_transactions": int((probabilities > 0.8).sum()),
        }

        # Alert on high fraud rate
        if metrics["fraud_rate"] > 0.15:
            self.logger.warning(
                f"High fraud rate detected: {metrics['fraud_rate']:.2%}"
            )

        if metrics["high_risk_transactions"] > 10:
            self.logger.warning(
                f"{metrics['high_risk_transactions']} high-risk transactions detected"
            )

        return metrics

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent_used": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "used": psutil.disk_usage("/").used,
                "percent_used": psutil.disk_usage("/").percent,
            },
        }

    def save_metrics(self, metrics: Dict[str, Any], filename: str):
        """Save metrics to JSON file."""
        filepath = self.log_dir / filename
        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2)
        self.logger.info(f"Metrics saved to {filepath}")

    def health_check(self) -> Dict[str, str]:
        """Perform system health check."""
        health = {"status": "healthy", "issues": []}

        # Check system resources
        if psutil.cpu_percent(interval=1) > 80:
            health["issues"].append("High CPU usage")
            health["status"] = "warning"

        if psutil.virtual_memory().percent > 85:
            health["issues"].append("High memory usage")
            health["status"] = "warning"

        if psutil.disk_usage("/").percent > 90:
            health["issues"].append("Low disk space")
            health["status"] = "critical"

        return health


if __name__ == "__main__":
    # Example usage
    monitor = FraudMonitor()

    # Test with sample data
    sample_data = pd.DataFrame(
        {
            "amount": np.random.uniform(10, 1000, 100),
            "is_fraudulent": np.random.choice([0, 1], 100, p=[0.9, 0.1]),
        }
    )

    data_quality = monitor.check_data_quality(sample_data)
    print("Data Quality:", json.dumps(data_quality, indent=2))

    system_health = monitor.health_check()
    print("System Health:", system_health)

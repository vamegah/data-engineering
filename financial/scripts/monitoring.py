"""
Production monitoring framework for Financial Analytics project.
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


class FinancialMonitor:
    """Monitor financial analytics system."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            filename=self.log_dir / "financial_monitoring.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def track_prediction_accuracy(
        self, predictions: np.ndarray, actuals: np.ndarray
    ) -> Dict[str, Any]:
        """Track LSTM model prediction accuracy."""
        mae = np.mean(np.abs(predictions - actuals))
        mse = np.mean((predictions - actuals) ** 2)
        rmse = np.sqrt(mse)

        # Directional accuracy
        pred_direction = np.sign(np.diff(predictions))
        actual_direction = np.sign(np.diff(actuals))
        directional_accuracy = np.mean(pred_direction == actual_direction)

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "directional_accuracy": float(directional_accuracy),
            "total_predictions": len(predictions),
        }

        if directional_accuracy < 0.5:
            self.logger.warning(f"Low directional accuracy: {directional_accuracy:.2%}")

        return metrics

    def check_market_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check market data quality."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(data),
            "missing_values": data.isnull().sum().to_dict(),
            "date_range": {
                "start": (
                    str(data.index.min())
                    if isinstance(data.index, pd.DatetimeIndex)
                    else None
                ),
                "end": (
                    str(data.index.max())
                    if isinstance(data.index, pd.DatetimeIndex)
                    else None
                ),
            },
        }

        if "Close" in data.columns:
            metrics["price_stats"] = {
                "mean": float(data["Close"].mean()),
                "std": float(data["Close"].std()),
                "min": float(data["Close"].min()),
                "max": float(data["Close"].max()),
            }

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

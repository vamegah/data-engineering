"""
Production monitoring framework for E-commerce Analytics project.
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


class EcommerceMonitor:
    """Monitor e-commerce analytics system."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            filename=self.log_dir / "ecommerce_monitoring.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def check_transaction_quality(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """Check transaction data quality."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_transactions": len(transactions),
            "missing_values": transactions.isnull().sum().to_dict(),
            "duplicate_transactions": transactions.duplicated().sum(),
        }

        if "total_amount" in transactions.columns:
            metrics["revenue_stats"] = {
                "total_revenue": float(transactions["total_amount"].sum()),
                "avg_order_value": float(transactions["total_amount"].mean()),
                "median_order_value": float(transactions["total_amount"].median()),
            }

        if metrics["duplicate_transactions"] > 0:
            self.logger.warning(
                f"Found {metrics['duplicate_transactions']} duplicate transactions"
            )

        return metrics

    def track_customer_metrics(self, customers: pd.DataFrame) -> Dict[str, Any]:
        """Track customer-related metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_customers": len(customers),
            "active_customers": (
                int(customers.get("active", pd.Series([0])).sum())
                if "active" in customers.columns
                else 0
            ),
        }

        if "tier" in customers.columns:
            metrics["customer_tiers"] = customers["tier"].value_counts().to_dict()

        return metrics

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }

    def health_check(self) -> Dict[str, str]:
        """System health check."""
        health = {"status": "healthy", "issues": []}

        if psutil.cpu_percent() > 80:
            health["issues"].append("High CPU usage")
            health["status"] = "warning"

        if psutil.virtual_memory().percent > 85:
            health["issues"].append("High memory usage")
            health["status"] = "warning"

        return health

"""
Production monitoring framework for Restaurant Analytics project.
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


class RestaurantMonitor:
    """Monitor restaurant analytics and sentiment analysis system."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            filename=self.log_dir / "restaurant_monitoring.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def check_review_data_quality(self, reviews: pd.DataFrame) -> Dict[str, Any]:
        """Check review data quality."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_reviews": len(reviews),
            "missing_values": reviews.isnull().sum().to_dict(),
            "duplicate_reviews": int(reviews.duplicated().sum()),
        }

        if "rating" in reviews.columns:
            metrics["rating_stats"] = {
                "mean_rating": float(reviews["rating"].mean()),
                "median_rating": float(reviews["rating"].median()),
                "rating_distribution": reviews["rating"].value_counts().to_dict(),
            }

        return metrics

    def track_sentiment_analysis(
        self, sentiments: pd.Series, confidences: np.ndarray
    ) -> Dict[str, Any]:
        """Track sentiment analysis performance."""
        sentiment_dist = sentiments.value_counts().to_dict()

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_analyses": len(sentiments),
            "sentiment_distribution": sentiment_dist,
            "positive_rate": float((sentiments == "positive").mean()),
            "negative_rate": float((sentiments == "negative").mean()),
            "avg_confidence": float(confidences.mean()),
            "low_confidence_count": int((confidences < 0.6).sum()),
        }

        # Alert on high negative sentiment
        if metrics["negative_rate"] > 0.3:
            self.logger.warning(
                f"High negative sentiment detected: {metrics['negative_rate']:.2%}"
            )

        # Alert on many low-confidence predictions
        if metrics["low_confidence_count"] > len(sentiments) * 0.2:
            self.logger.warning(
                f"Many low-confidence predictions: {metrics['low_confidence_count']}"
            )

        return metrics

    def track_review_velocity(
        self, reviews: pd.DataFrame, time_column: str = "date"
    ) -> Dict[str, Any]:
        """Track review velocity over time."""
        if time_column not in reviews.columns:
            return {}

        reviews[time_column] = pd.to_datetime(reviews[time_column])
        reviews_per_day = reviews.groupby(reviews[time_column].dt.date).size()

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "avg_reviews_per_day": float(reviews_per_day.mean()),
            "max_reviews_per_day": int(reviews_per_day.max()),
            "min_reviews_per_day": int(reviews_per_day.min()),
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

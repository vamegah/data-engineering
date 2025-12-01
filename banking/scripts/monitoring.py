"""
Monitoring Framework for Banking Churn Prediction
Tracks data quality, model performance, and system metrics
"""

import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import warnings

warnings.filterwarnings("ignore")


class DataQualityMonitor:
    """Monitor data quality metrics and detect anomalies"""

    def __init__(self, log_dir: str = "../logs/monitoring"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self.logger = logging.getLogger("DataQualityMonitor")
        self.logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(self.log_dir / "data_quality.log")
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def check_data_quality(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """
        Comprehensive data quality check

        Args:
            df: DataFrame to check
            dataset_name: Name of the dataset

        Returns:
            Dictionary with quality metrics
        """
        self.logger.info(f"Running quality check for {dataset_name}")

        metrics = {
            "dataset": dataset_name,
            "timestamp": datetime.now().isoformat(),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": {},
            "duplicates": 0,
            "data_types": {},
            "numeric_stats": {},
            "alerts": [],
        }

        # Missing values check
        missing = df.isnull().sum()
        for col in df.columns:
            missing_count = int(missing[col])
            missing_pct = (missing_count / len(df)) * 100
            metrics["missing_values"][col] = {
                "count": missing_count,
                "percentage": round(missing_pct, 2),
            }

            if missing_pct > 5:
                alert = f"High missing values in {col}: {missing_pct:.2f}%"
                metrics["alerts"].append(alert)
                self.logger.warning(alert)

        # Duplicate check
        duplicates = df.duplicated().sum()
        metrics["duplicates"] = int(duplicates)
        if duplicates > 0:
            alert = f"Found {duplicates} duplicate rows"
            metrics["alerts"].append(alert)
            self.logger.warning(alert)

        # Data types
        for col in df.columns:
            metrics["data_types"][col] = str(df[col].dtype)

        # Numeric statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            metrics["numeric_stats"][col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "median": float(df[col].median()),
            }

        # Save metrics
        self._save_metrics(metrics, dataset_name)

        self.logger.info(
            f"Quality check completed for {dataset_name}: "
            f"{len(metrics['alerts'])} alerts found"
        )

        return metrics

    def detect_data_drift(
        self,
        current_df: pd.DataFrame,
        baseline_df: pd.DataFrame,
        numeric_cols: List[str],
    ) -> Dict[str, Any]:
        """
        Detect data drift by comparing distributions

        Args:
            current_df: Current dataset
            baseline_df: Baseline dataset for comparison
            numeric_cols: Numeric columns to check

        Returns:
            Dictionary with drift metrics
        """
        self.logger.info("Detecting data drift")

        drift_metrics = {
            "timestamp": datetime.now().isoformat(),
            "columns_checked": numeric_cols,
            "drift_detected": [],
            "drift_scores": {},
        }

        for col in numeric_cols:
            if col not in current_df.columns or col not in baseline_df.columns:
                continue

            # Calculate drift score (normalized difference in means)
            current_mean = current_df[col].mean()
            baseline_mean = baseline_df[col].mean()
            baseline_std = baseline_df[col].std()

            if baseline_std > 0:
                drift_score = abs(current_mean - baseline_mean) / baseline_std
                drift_metrics["drift_scores"][col] = round(float(drift_score), 4)

                # Alert if drift > 2 standard deviations
                if drift_score > 2:
                    drift_metrics["drift_detected"].append(
                        {
                            "column": col,
                            "drift_score": round(float(drift_score), 4),
                            "current_mean": round(float(current_mean), 2),
                            "baseline_mean": round(float(baseline_mean), 2),
                        }
                    )
                    self.logger.warning(
                        f"Data drift detected in {col}: " f"score={drift_score:.4f}"
                    )

        self._save_metrics(drift_metrics, "data_drift")

        return drift_metrics

    def _save_metrics(self, metrics: Dict[str, Any], name: str):
        """Save metrics to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.log_dir / f"{name}_{timestamp}.json"

        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2)

        self.logger.info(f"Metrics saved to {filepath}")


class ModelPerformanceMonitor:
    """Monitor ML model performance and predictions"""

    def __init__(self, log_dir: str = "../logs/monitoring"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self.logger = logging.getLogger("ModelPerformanceMonitor")
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler(self.log_dir / "model_performance.log")
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def track_predictions(
        self,
        predictions: np.ndarray,
        probabilities: np.ndarray,
        actual: np.ndarray = None,
    ) -> Dict[str, Any]:
        """
        Track prediction distribution and performance

        Args:
            predictions: Binary predictions
            probabilities: Prediction probabilities
            actual: Actual labels (optional)

        Returns:
            Dictionary with prediction metrics
        """
        self.logger.info("Tracking predictions")

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(predictions),
            "prediction_distribution": {
                "positive": int(predictions.sum()),
                "negative": int(len(predictions) - predictions.sum()),
                "positive_rate": float(predictions.mean()),
            },
            "probability_stats": {
                "mean": float(probabilities.mean()),
                "std": float(probabilities.std()),
                "min": float(probabilities.min()),
                "max": float(probabilities.max()),
                "median": float(np.median(probabilities)),
            },
            "alerts": [],
        }

        # Check for prediction anomalies
        if metrics["prediction_distribution"]["positive_rate"] > 0.5:
            alert = f"High positive prediction rate: {metrics['prediction_distribution']['positive_rate']:.2%}"
            metrics["alerts"].append(alert)
            self.logger.warning(alert)

        if metrics["prediction_distribution"]["positive_rate"] < 0.05:
            alert = f"Very low positive prediction rate: {metrics['prediction_distribution']['positive_rate']:.2%}"
            metrics["alerts"].append(alert)
            self.logger.warning(alert)

        # If actual labels provided, calculate accuracy
        if actual is not None:
            from sklearn.metrics import (
                accuracy_score,
                precision_score,
                recall_score,
                f1_score,
            )

            metrics["performance"] = {
                "accuracy": float(accuracy_score(actual, predictions)),
                "precision": float(precision_score(actual, predictions)),
                "recall": float(recall_score(actual, predictions)),
                "f1_score": float(f1_score(actual, predictions)),
            }

            # Alert if accuracy drops
            if metrics["performance"]["accuracy"] < 0.75:
                alert = (
                    f"Low accuracy detected: {metrics['performance']['accuracy']:.2%}"
                )
                metrics["alerts"].append(alert)
                self.logger.warning(alert)

        # Save metrics
        self._save_metrics(metrics)

        return metrics

    def track_inference_time(
        self, start_time: float, end_time: float, num_predictions: int
    ) -> Dict[str, float]:
        """
        Track model inference time

        Args:
            start_time: Start timestamp
            end_time: End timestamp
            num_predictions: Number of predictions made

        Returns:
            Dictionary with timing metrics
        """
        total_time = end_time - start_time
        avg_time = total_time / num_predictions if num_predictions > 0 else 0

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_time_seconds": round(total_time, 4),
            "num_predictions": num_predictions,
            "avg_time_per_prediction_ms": round(avg_time * 1000, 2),
        }

        # Alert if inference is slow
        if avg_time > 0.1:  # 100ms threshold
            self.logger.warning(
                f"Slow inference detected: {avg_time*1000:.2f}ms per prediction"
            )

        self.logger.info(
            f"Inference completed: {num_predictions} predictions "
            f"in {total_time:.4f}s ({avg_time*1000:.2f}ms avg)"
        )

        return metrics

    def _save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.log_dir / f"predictions_{timestamp}.json"

        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2)


class SystemMetricsMonitor:
    """Monitor system resources and application health"""

    def __init__(self, log_dir: str = "../logs/monitoring"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("SystemMetricsMonitor")
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler(self.log_dir / "system_metrics.log")
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics

        Returns:
            Dictionary with system metrics
        """
        import psutil

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total_mb": round(psutil.virtual_memory().total / (1024**2), 2),
                "available_mb": round(psutil.virtual_memory().available / (1024**2), 2),
                "percent_used": psutil.virtual_memory().percent,
            },
            "disk": {
                "total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
                "used_gb": round(psutil.disk_usage("/").used / (1024**3), 2),
                "percent_used": psutil.disk_usage("/").percent,
            },
        }

        # Alerts
        if metrics["cpu_percent"] > 80:
            self.logger.warning(f"High CPU usage: {metrics['cpu_percent']}%")

        if metrics["memory"]["percent_used"] > 85:
            self.logger.warning(
                f"High memory usage: {metrics['memory']['percent_used']}%"
            )

        if metrics["disk"]["percent_used"] > 90:
            self.logger.warning(f"High disk usage: {metrics['disk']['percent_used']}%")

        return metrics

    def health_check(self) -> Dict[str, Any]:
        """
        Application health check

        Returns:
            Health status dictionary
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
        }

        # Check data files exist
        data_files = [
            "../data/processed/banking_customers_clean.csv",
            "../data/processed/banking_transactions_clean.csv",
        ]

        for file in data_files:
            exists = Path(file).exists()
            health["checks"][f"data_file_{Path(file).name}"] = (
                "ok" if exists else "missing"
            )
            if not exists:
                health["status"] = "degraded"
                self.logger.warning(f"Data file missing: {file}")

        # Check model file
        model_path = Path("../models/churn_model.pkl")
        health["checks"]["model_file"] = "ok" if model_path.exists() else "missing"
        if not model_path.exists():
            health["status"] = "degraded"
            self.logger.warning("Model file missing")

        # Check log directory
        health["checks"]["log_directory"] = "ok" if self.log_dir.exists() else "missing"

        return health


# Convenience function for easy monitoring
def monitor_etl_pipeline(
    customers_df: pd.DataFrame, transactions_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Monitor ETL pipeline execution

    Args:
        customers_df: Processed customers DataFrame
        transactions_df: Processed transactions DataFrame

    Returns:
        Combined monitoring metrics
    """
    data_monitor = DataQualityMonitor()

    # Check data quality
    customer_metrics = data_monitor.check_data_quality(customers_df, "customers")
    transaction_metrics = data_monitor.check_data_quality(
        transactions_df, "transactions"
    )

    return {
        "customers": customer_metrics,
        "transactions": transaction_metrics,
        "timestamp": datetime.now().isoformat(),
    }


def monitor_model_predictions(
    y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray
) -> Dict[str, Any]:
    """
    Monitor model predictions

    Args:
        y_true: Actual labels
        y_pred: Predicted labels
        y_prob: Prediction probabilities

    Returns:
        Prediction monitoring metrics
    """
    model_monitor = ModelPerformanceMonitor()
    return model_monitor.track_predictions(y_pred, y_prob, y_true)


if __name__ == "__main__":
    # Example usage
    print("🔍 Banking Churn Monitoring Framework")
    print("=" * 50)

    # System health check
    system_monitor = SystemMetricsMonitor()
    health = system_monitor.health_check()
    print(f"\n✅ Health Status: {health['status']}")
    print(f"Checks: {health['checks']}")

    # System metrics
    metrics = system_monitor.get_system_metrics()
    print(f"\n📊 System Metrics:")
    print(f"CPU Usage: {metrics['cpu_percent']}%")
    print(f"Memory Usage: {metrics['memory']['percent_used']}%")
    print(f"Disk Usage: {metrics['disk']['percent_used']}%")

    print("\n✅ Monitoring framework initialized!")
    print(f"Logs saved to: ../logs/monitoring/")

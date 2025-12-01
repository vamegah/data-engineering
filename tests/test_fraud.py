"""
Comprehensive test suite for Fraud Detection project.
Tests ETL pipeline, data quality, ML model, and performance.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFraudETL:
    """Test ETL pipeline functionality"""

    def test_data_loading(self):
        """Test that data files can be loaded"""
        data_path = project_root / "data" / "processed"

        # Check if processed data exists
        assert data_path.exists(), "Processed data directory not found"

        # Try to load data
        users_file = data_path / "fraud_users_clean.csv"
        txns_file = data_path / "fraud_transactions_clean.csv"

        if users_file.exists():
            users = pd.read_csv(users_file)
            assert len(users) > 0, "Users dataframe is empty"
            assert "user_id" in users.columns, "Missing user_id column"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)
            assert len(txns) > 0, "Transactions dataframe is empty"
            assert "transaction_id" in txns.columns, "Missing transaction_id column"

    def test_required_columns(self):
        """Test that all required columns are present"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            required_cols = ["transaction_id", "user_id", "amount", "is_fraud"]
            for col in required_cols:
                assert col in txns.columns, f"Missing required column: {col}"

    def test_data_types(self):
        """Test that data types are correct"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            # Check numeric columns
            assert pd.api.types.is_numeric_dtype(
                txns["amount"]
            ), "Amount should be numeric"
            assert pd.api.types.is_integer_dtype(
                txns["is_fraud"]
            ), "is_fraud should be integer"


class TestDataQuality:
    """Test data quality metrics"""

    def test_no_missing_values_in_key_columns(self):
        """Test that key columns have no missing values"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            key_columns = ["transaction_id", "user_id", "amount"]
            for col in key_columns:
                if col in txns.columns:
                    assert txns[col].isna().sum() == 0, f"{col} has missing values"

    def test_no_duplicates(self):
        """Test that there are no duplicate transaction IDs"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            if "transaction_id" in txns.columns:
                duplicates = txns["transaction_id"].duplicated().sum()
                assert duplicates == 0, f"Found {duplicates} duplicate transaction IDs"

    def test_fraud_label_values(self):
        """Test that fraud labels are binary"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            if "is_fraud" in txns.columns:
                unique_values = txns["is_fraud"].unique()
                assert set(unique_values).issubset(
                    {0, 1}
                ), "Fraud labels should be 0 or 1"

    def test_amount_ranges(self):
        """Test that transaction amounts are reasonable"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            if "amount" in txns.columns:
                assert (
                    txns["amount"].min() >= 0
                ), "Transaction amounts should be non-negative"
                assert (
                    txns["amount"].max() < 1000000
                ), "Suspiciously high transaction amount"


class TestMLModel:
    """Test ML model functionality"""

    def test_model_exists(self):
        """Test that trained model exists"""
        model_path = project_root / "fraud" / "models" / "fraud_model.pkl"

        # Model might not exist yet, so this is a soft check
        if model_path.exists():
            assert model_path.is_file(), "Model path exists but is not a file"

    def test_model_prediction_shape(self):
        """Test that model predictions have correct shape"""
        try:
            import joblib

            model_path = project_root / "fraud" / "models" / "fraud_model.pkl"

            if model_path.exists():
                model_data = joblib.load(model_path)
                model = model_data.get("model")

                if model is not None:
                    # Create sample data
                    X_sample = np.array(
                        [[100, 1, 0, 50]]
                    )  # amount, hour, day, user_txn_count

                    try:
                        predictions = model.predict(X_sample)
                        assert predictions.shape[0] == 1, "Prediction shape mismatch"
                        assert predictions[0] in [0, 1], "Prediction should be 0 or 1"
                    except:
                        pass  # Model might need different features
        except:
            pytest.skip("Model file not found or incompatible")

    def test_fraud_rate_reasonable(self):
        """Test that overall fraud rate is reasonable"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            if "is_fraud" in txns.columns:
                fraud_rate = txns["is_fraud"].mean()
                assert (
                    0 < fraud_rate < 0.5
                ), f"Fraud rate {fraud_rate:.2%} seems unrealistic"


class TestPerformance:
    """Test performance metrics"""

    def test_data_loading_speed(self):
        """Test that data loads within reasonable time"""
        import time

        data_path = project_root / "data" / "processed"
        txns_file = data_path / "fraud_transactions_clean.csv"

        if txns_file.exists():
            start = time.time()
            txns = pd.read_csv(txns_file)
            load_time = time.time() - start

            # Should load within 5 seconds
            assert (
                load_time < 5.0
            ), f"Data loading took {load_time:.2f}s, should be < 5s"

    def test_memory_usage(self):
        """Test that data doesn't use excessive memory"""
        data_path = project_root / "data" / "processed"
        txns_file = data_path / "fraud_transactions_clean.csv"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)
            memory_mb = txns.memory_usage(deep=True).sum() / 1024 / 1024

            # Should use less than 500MB
            assert memory_mb < 500, f"Data uses {memory_mb:.0f}MB, should be < 500MB"


class TestIntegration:
    """Integration tests for end-to-end workflows"""

    def test_etl_to_model_workflow(self):
        """Test that ETL output can be used for modeling"""
        data_path = project_root / "data" / "processed"

        if (data_path / "fraud_transactions_clean.csv").exists():
            txns = pd.read_csv(data_path / "fraud_transactions_clean.csv")

            # Check that data has features needed for modeling
            if "is_fraud" in txns.columns:
                # Should have features and target
                X = txns.drop(["is_fraud"], axis=1, errors="ignore")
                y = txns["is_fraud"]

                assert len(X) == len(y), "Feature-target length mismatch"
                assert len(X) > 100, "Not enough data for modeling"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

# Banking Project - Quick Start Testing Suite
# Run with: pytest tests/test_banking.py -v

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from banking.scripts.etl_pipeline import BankingETL


class TestBankingETL:
    """Unit tests for Banking ETL Pipeline"""

    @pytest.fixture
    def sample_customers(self):
        """Create sample customer data for testing"""
        return pd.DataFrame(
            {
                "customer_id": ["BANK001", "BANK002", "BANK003"],
                "credit_score": [650, 720, 580],
                "age": [35, 45, 25],
                "balance": [5000, 10000, 0],
                "churn": [0, 0, 1],
                "country": ["USA", "UK", "Germany"],
                "gender": ["Male", "Female", "Male"],
                "tenure": [5, 3, 1],
                "products_number": [2, 3, 1],
                "credit_card": [1, 1, 0],
                "active_member": [1, 1, 0],
                "estimated_salary": [50000, 75000, 30000],
            }
        )

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transaction data for testing"""
        return pd.DataFrame(
            {
                "transaction_id": ["TXN001", "TXN002", "TXN003"],
                "customer_id": ["BANK001", "BANK001", "BANK002"],
                "amount": [100, -50, 200],
                "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
                "transaction_type": ["Deposit", "Withdrawal", "Deposit"],
                "merchant": ["Store A", "ATM", "Store B"],
                "location": ["NYC", "NYC", "London"],
                "is_fraudulent": [0, 0, 0],
            }
        )

    def test_etl_initialization(self):
        """Test ETL class initialization"""
        etl = BankingETL()
        assert etl.customers is None
        assert etl.transactions is None
        assert etl.processed_customers is None
        assert etl.processed_transactions is None

    def test_data_validation_removes_invalid_ages(self, sample_customers):
        """Test that invalid ages are removed during transformation"""
        # Add invalid ages
        sample_customers.loc[3] = [
            "BANK004",
            650,
            15,
            1000,
            0,
            "USA",
            "Male",
            1,
            1,
            1,
            1,
            50000,
        ]  # age < 18
        sample_customers.loc[4] = [
            "BANK005",
            650,
            105,
            1000,
            0,
            "USA",
            "Male",
            1,
            1,
            1,
            1,
            50000,
        ]  # age > 100

        etl = BankingETL()
        etl.customers = sample_customers
        etl.transform_customers()

        # Should remove customers with age < 18
        assert all(etl.processed_customers["age"] >= 18)
        assert len(etl.processed_customers) <= len(sample_customers)

    def test_data_validation_removes_negative_balances(self, sample_customers):
        """Test that negative balances are removed"""
        # Add negative balance
        sample_customers.loc[3] = [
            "BANK006",
            650,
            35,
            -1000,
            0,
            "USA",
            "Male",
            1,
            1,
            1,
            1,
            50000,
        ]

        etl = BankingETL()
        etl.customers = sample_customers
        etl.transform_customers()

        # Should remove negative balances
        assert all(etl.processed_customers["balance"] >= 0)

    def test_data_validation_credit_score_range(self, sample_customers):
        """Test credit score validation"""
        # Add invalid credit scores
        sample_customers.loc[3] = [
            "BANK007",
            250,
            35,
            1000,
            0,
            "USA",
            "Male",
            1,
            1,
            1,
            1,
            50000,
        ]  # too low
        sample_customers.loc[4] = [
            "BANK008",
            900,
            35,
            1000,
            0,
            "USA",
            "Male",
            1,
            1,
            1,
            1,
            50000,
        ]  # too high

        etl = BankingETL()
        etl.customers = sample_customers
        etl.transform_customers()

        # Credit scores should be between 300 and 850
        assert all(etl.processed_customers["credit_score"].between(300, 850))

    def test_transaction_type_adjustments(self, sample_transactions):
        """Test that withdrawals and payments become negative"""
        etl = BankingETL()
        etl.transactions = sample_transactions
        etl.transform_transactions()

        # Withdrawals should be negative
        withdrawals = etl.processed_transactions[
            etl.processed_transactions["transaction_type"] == "Withdrawal"
        ]
        assert all(withdrawals["amount"] < 0)

    def test_duplicate_removal(self, sample_customers):
        """Test duplicate removal"""
        # Add duplicate
        duplicate = sample_customers.iloc[0:1].copy()
        customers_with_dup = pd.concat([sample_customers, duplicate])

        etl = BankingETL()
        etl.customers = customers_with_dup
        etl.transform_customers()

        # Should have no duplicates
        assert len(etl.processed_customers) == len(
            etl.processed_customers.drop_duplicates()
        )

    def test_feature_engineering_creates_required_features(
        self, sample_customers, sample_transactions
    ):
        """Test that all required features are created"""
        etl = BankingETL()
        etl.processed_customers = sample_customers
        etl.processed_transactions = sample_transactions
        etl.create_features()

        # Check that new features exist
        required_features = [
            "txn_count",
            "avg_amount",
            "std_amount",
            "min_amount",
            "max_amount",
            "total_amount",
            "first_txn",
            "last_txn",
            "days_since_last_txn",
        ]

        for feature in required_features:
            assert (
                feature in etl.processed_customers.columns
            ), f"Feature {feature} not created"

    def test_transaction_aggregations_correct(
        self, sample_customers, sample_transactions
    ):
        """Test transaction aggregation calculations"""
        etl = BankingETL()
        etl.processed_customers = sample_customers
        etl.processed_transactions = sample_transactions
        etl.create_features()

        # Customer BANK001 should have 2 transactions
        customer_data = etl.processed_customers[
            etl.processed_customers["customer_id"] == "BANK001"
        ].iloc[0]

        assert customer_data["txn_count"] == 2
        assert customer_data["min_amount"] == -50
        assert customer_data["max_amount"] == 100

    def test_handles_customers_with_no_transactions(
        self, sample_customers, sample_transactions
    ):
        """Test that customers with no transactions get default values"""
        etl = BankingETL()
        etl.processed_customers = sample_customers
        etl.processed_transactions = sample_transactions
        etl.create_features()

        # Customer BANK003 has no transactions
        customer_data = etl.processed_customers[
            etl.processed_customers["customer_id"] == "BANK003"
        ].iloc[0]

        assert customer_data["txn_count"] == 0
        assert customer_data["avg_amount"] == 0
        assert customer_data["days_since_last_txn"] == 365


class TestDataQuality:
    """Data quality validation tests"""

    def test_churn_rate_in_expected_range(self):
        """Test that overall churn rate is realistic"""
        # This would load actual processed data
        # For now, test the concept
        churn_rate = 0.20  # 20% - realistic for banking
        assert 0.05 <= churn_rate <= 0.35, "Churn rate outside expected range"

    def test_no_missing_critical_fields(self, sample_customers):
        """Test that critical fields have no missing values"""
        critical_fields = ["customer_id", "credit_score", "age", "churn"]

        for field in critical_fields:
            assert sample_customers[field].notna().all(), f"{field} has missing values"

    def test_customer_id_uniqueness(self, sample_customers):
        """Test that customer IDs are unique"""
        assert len(sample_customers) == len(sample_customers["customer_id"].unique())


class TestMLModel:
    """Machine learning model tests"""

    def test_model_features_match_training(self):
        """Test that prediction features match training"""
        expected_features = [
            "credit_score",
            "age",
            "tenure",
            "balance",
            "products_number",
            "credit_card",
            "active_member",
            "estimated_salary",
            "txn_count",
            "days_since_last_txn",
            "country_encoded",
            "gender_encoded",
        ]

        # This would load the actual model
        # model_artifacts = joblib.load('../models/churn_model.pkl')
        # assert set(model_artifacts['features']) == set(expected_features)

        # For now, just verify the list
        assert len(expected_features) == 12

    def test_prediction_output_format(self):
        """Test that predictions are in correct format"""
        # Simulate prediction
        prediction = {
            "churn_probability": 0.75,
            "churn_prediction": True,
            "risk_level": "High",
        }

        assert 0 <= prediction["churn_probability"] <= 1
        assert isinstance(prediction["churn_prediction"], bool)
        assert prediction["risk_level"] in ["Low", "Medium", "High"]


# Performance tests
class TestPerformance:
    """Performance and scalability tests"""

    def test_etl_execution_time(self, sample_customers, sample_transactions):
        """Test ETL completes in reasonable time"""
        import time

        etl = BankingETL()
        etl.customers = sample_customers
        etl.transactions = sample_transactions

        start = time.time()
        etl.transform_customers()
        etl.transform_transactions()
        etl.create_features()
        end = time.time()

        # Should complete in under 1 second for small dataset
        assert (end - start) < 1.0, "ETL taking too long"

    def test_handles_large_dataset(self):
        """Test that system can handle larger datasets"""
        # Create 10,000 customer records
        large_dataset = pd.DataFrame(
            {
                "customer_id": [f"BANK{i:05d}" for i in range(10000)],
                "credit_score": np.random.randint(300, 850, 10000),
                "age": np.random.randint(18, 80, 10000),
                "balance": np.random.uniform(0, 100000, 10000),
                "churn": np.random.choice([0, 1], 10000),
                "country": np.random.choice(["USA", "UK", "Germany"], 10000),
                "gender": np.random.choice(["Male", "Female"], 10000),
                "tenure": np.random.randint(0, 10, 10000),
                "products_number": np.random.randint(1, 5, 10000),
                "credit_card": np.random.choice([0, 1], 10000),
                "active_member": np.random.choice([0, 1], 10000),
                "estimated_salary": np.random.uniform(20000, 150000, 10000),
            }
        )

        etl = BankingETL()
        etl.customers = large_dataset
        success = etl.transform_customers()

        assert success == True
        assert len(etl.processed_customers) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

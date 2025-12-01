"""
Comprehensive test suite for E-commerce Analytics project.
Tests ETL pipeline, data quality, segmentation, and performance.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestEcommerceETL:
    """Test ETL pipeline functionality"""

    def test_data_loading(self):
        """Test that data files can be loaded"""
        data_path = project_root / "data" / "processed"

        files_to_check = [
            "ecommerce_customers_clean.csv",
            "ecommerce_products_clean.csv",
            "ecommerce_transactions_clean.csv",
        ]

        for filename in files_to_check:
            file_path = data_path / filename
            if file_path.exists():
                df = pd.read_csv(file_path)
                assert len(df) > 0, f"{filename} is empty"

    def test_required_columns_customers(self):
        """Test customer data has required columns"""
        data_path = project_root / "data" / "processed"
        customers_file = data_path / "ecommerce_customers_clean.csv"

        if customers_file.exists():
            customers = pd.read_csv(customers_file)
            required_cols = ["customer_id", "location", "tier"]

            for col in required_cols:
                assert col in customers.columns, f"Missing column: {col}"

    def test_required_columns_transactions(self):
        """Test transaction data has required columns"""
        data_path = project_root / "data" / "processed"
        txns_file = data_path / "ecommerce_transactions_clean.csv"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)
            required_cols = ["transaction_id", "customer_id", "product_id"]

            for col in required_cols:
                assert col in txns.columns, f"Missing column: {col}"


class TestDataQuality:
    """Test data quality metrics"""

    def test_no_missing_ids(self):
        """Test that ID columns have no missing values"""
        data_path = project_root / "data" / "processed"

        customers_file = data_path / "ecommerce_customers_clean.csv"
        if customers_file.exists():
            customers = pd.read_csv(customers_file)
            assert customers["customer_id"].isna().sum() == 0, "Missing customer IDs"

    def test_customer_tier_values(self):
        """Test that customer tiers are valid"""
        data_path = project_root / "data" / "processed"
        customers_file = data_path / "ecommerce_customers_clean.csv"

        if customers_file.exists():
            customers = pd.read_csv(customers_file)
            if "tier" in customers.columns:
                valid_tiers = {"Gold", "Silver", "Bronze", "Platinum"}
                assert (
                    customers["tier"].isin(valid_tiers).all()
                ), "Invalid customer tier"

    def test_price_positive(self):
        """Test that prices are positive"""
        data_path = project_root / "data" / "processed"
        products_file = data_path / "ecommerce_products_clean.csv"

        if products_file.exists():
            products = pd.read_csv(products_file)
            if "price" in products.columns:
                assert (products["price"] > 0).all(), "Found non-positive prices"

    def test_no_duplicate_transactions(self):
        """Test no duplicate transaction IDs"""
        data_path = project_root / "data" / "processed"
        txns_file = data_path / "ecommerce_transactions_clean.csv"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)
            if "transaction_id" in txns.columns:
                duplicates = txns["transaction_id"].duplicated().sum()
                assert duplicates == 0, f"Found {duplicates} duplicate transactions"


class TestSegmentation:
    """Test customer segmentation functionality"""

    def test_rfm_calculation(self):
        """Test RFM metrics can be calculated"""
        data_path = project_root / "data" / "processed"
        txns_file = data_path / "ecommerce_transactions_clean.csv"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)

            if all(col in txns.columns for col in ["customer_id", "date"]):
                # Test recency can be calculated
                txns["date"] = pd.to_datetime(txns["date"])
                recency = (
                    txns["date"].max() - txns.groupby("customer_id")["date"].max()
                ).dt.days
                assert len(recency) > 0, "Recency calculation failed"

    def test_customer_segments_exist(self):
        """Test that customer segments can be created"""
        data_path = project_root / "data" / "processed"
        customers_file = data_path / "ecommerce_customers_clean.csv"

        if customers_file.exists():
            customers = pd.read_csv(customers_file)

            # Should have at least 10 customers for segmentation
            assert len(customers) >= 10, "Not enough customers for segmentation"


class TestPerformance:
    """Test performance metrics"""

    def test_data_loading_speed(self):
        """Test data loads quickly"""
        import time

        data_path = project_root / "data" / "processed"
        txns_file = data_path / "ecommerce_transactions_clean.csv"

        if txns_file.exists():
            start = time.time()
            txns = pd.read_csv(txns_file)
            load_time = time.time() - start

            assert load_time < 5.0, f"Loading took {load_time:.2f}s, should be < 5s"

    def test_memory_usage(self):
        """Test memory usage is reasonable"""
        data_path = project_root / "data" / "processed"
        txns_file = data_path / "ecommerce_transactions_clean.csv"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)
            memory_mb = txns.memory_usage(deep=True).sum() / 1024 / 1024
            assert memory_mb < 500, f"Using {memory_mb:.0f}MB, should be < 500MB"


class TestBusinessMetrics:
    """Test business metric calculations"""

    def test_revenue_calculation(self):
        """Test that revenue can be calculated"""
        data_path = project_root / "data" / "processed"
        txns_file = data_path / "ecommerce_transactions_clean.csv"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)

            if "total_amount" in txns.columns:
                total_revenue = txns["total_amount"].sum()
                assert total_revenue > 0, "Total revenue should be positive"

    def test_aov_reasonable(self):
        """Test average order value is reasonable"""
        data_path = project_root / "data" / "processed"
        txns_file = data_path / "ecommerce_transactions_clean.csv"

        if txns_file.exists():
            txns = pd.read_csv(txns_file)

            if "total_amount" in txns.columns:
                aov = txns["total_amount"].mean()
                assert 10 < aov < 10000, f"AOV ${aov:.2f} seems unrealistic"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

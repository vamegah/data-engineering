#!/usr/bin/env python3
"""
Test script for shared components
"""

import sys
import os

# Add shared modules to path
sys.path.append("shared")

from config.database import DatabaseConfig, test_database_connection
from utils.helpers import DataValidator, VisualizationHelper, BusinessMetrics
from utils.helpers import setup_environment, validate_data
import pandas as pd
import numpy as np


def test_database():
    """Test database configuration"""
    print("🧪 Testing Database Configuration...")

    try:
        # Test connection
        if test_database_connection():
            print("✅ Database connection: SUCCESS")
        else:
            print("❌ Database connection: FAILED")
            return False

        # Test configuration
        db_config = DatabaseConfig()
        conn_str = db_config.get_connection_string()
        print(f"✅ Connection string: {conn_str}")

        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_helpers():
    """Test helper functions"""
    print("\n🧪 Testing Helper Functions...")

    try:
        # Create test data
        test_data = pd.DataFrame(
            {
                "sales": [100, 200, 300, None, 500],
                "customers": [10, 20, 30, 40, 50],
                "region": ["North", "South", "North", "East", "West"],
                "date": pd.date_range("2023-01-01", periods=5),
            }
        )

        # Test validation
        report = validate_data(test_data, "Test Data")
        print("✅ Data validation: SUCCESS")

        # Test visualization setup
        VisualizationHelper.setup_plotting()
        print("✅ Visualization setup: SUCCESS")

        # Test business metrics
        metrics = BusinessMetrics.calculate_financial_metrics(
            test_data, "sales", "date"
        )
        print("✅ Business metrics: SUCCESS")

        # Test data processing
        from utils.helpers import DataProcessor

        cleaned_data = DataProcessor.clean_column_names(test_data)
        print("✅ Data processing: SUCCESS")

        return True

    except Exception as e:
        print(f"❌ Helpers test failed: {e}")
        return False


def test_database_setup():
    """Test database setup script"""
    print("\n🧪 Testing Database Setup...")

    try:
        from scripts.database_setup import DatabaseSetup

        setup = DatabaseSetup("development")
        tables = setup.get_table_info()

        if tables:
            print("✅ Database setup: SUCCESS")
            print(f"   Found {len(tables)} tables")
        else:
            print("❌ Database setup: FAILED - No tables found")
            return False

        return True

    except Exception as e:
        print(f"❌ Database setup test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Shared Components")
    print("=" * 50)

    tests = [test_database, test_helpers, test_database_setup]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {i}. {test.__name__}: {status}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All shared components are working correctly!")
        return True
    else:
        print("💡 Some tests failed. Please check your setup.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

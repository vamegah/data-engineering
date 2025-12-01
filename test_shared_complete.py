#!/usr/bin/env python3
"""
Complete test script for all shared components
"""

import sys
import os
import pandas as pd

# Add shared modules to path
sys.path.append('shared')

def test_all_components():
    """Test all shared components"""
    print("🚀 Testing All Shared Components")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Database Configuration
    try:
        from shared.config.database import DatabaseConfig, test_database_connection
        
        db_config = DatabaseConfig('development')
        conn_str = db_config.get_connection_string()
        
        if test_database_connection():
            print("✅ Database Configuration: PASS")
            tests_passed += 1
        else:
            print("❌ Database Configuration: FAIL - Could not connect to database")
        total_tests += 1
        
    except Exception as e:
        print(f"❌ Database Configuration: FAIL - {e}")
        total_tests += 1
    
    # Test 2: Helper Functions
    try:
        from shared.utils.helpers import DataValidator, VisualizationHelper, BusinessMetrics
        
        # Test data validation
        test_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        report = DataValidator.validate_dataframe(test_df, "Test Data")
        
        # Test visualization setup
        VisualizationHelper.setup_plotting()
        
        # Test business metrics
        metrics_df = pd.DataFrame({'sales': [100, 200, 300], 'date': pd.date_range('2023-01-01', periods=3)})
        metrics = BusinessMetrics.calculate_financial_metrics(metrics_df, 'sales', 'date')
        
        print("✅ Helper Functions: PASS")
        tests_passed += 1
        
    except Exception as e:
        print(f"❌ Helper Functions: FAIL - {e}")
    total_tests += 1
    
    # Test 3: Data Generator
    try:
        from shared.utils.data_generator import MockDataGenerator, test_data_generation
        
        if test_data_generation():
            print("✅ Data Generator: PASS")
            tests_passed += 1
        else:
            print("❌ Data Generator: FAIL")
        total_tests += 1
    except Exception as e:
        print(f"❌ Data Generator: FAIL - {e}")
        total_tests += 1
    
    # Test 4: Database Setup
    try:
        from shared.scripts.database_setup import DatabaseSetup
        
        setup = DatabaseSetup('development')
        tables = setup.get_table_info()
        
        if tables:
            print("✅ Database Setup: PASS")
            tests_passed += 1
        else:
            print("❌ Database Setup: FAIL - No tables found")
        total_tests += 1
    except Exception as e:
        print(f"❌ Database Setup: FAIL - {e}")
        total_tests += 1
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All shared components are working correctly!")
        return True
    else:
        print("💡 Some components need attention.")
        return False

def generate_sample_data():
    """Generate a small sample of all datasets"""
    print("\n🎯 Generating Sample Data...")
    
    try:
        from shared.utils.data_generator import MockDataGenerator
        
        generator = MockDataGenerator(42)
        
        # Generate small samples
        print("📊 E-commerce sample...")
        customers, products, transactions = generator.generate_ecommerce_data(100, 20, 500)
        print(f"   Customers: {len(customers)}, Products: {len(products)}, Transactions: {len(transactions)}")
        
        print("🏥 Healthcare sample...")
        patients, treatments, facilities = generator.generate_healthcare_data(200, 500, 10)
        print(f"   Patients: {len(patients)}, Treatments: {len(treatments)}, Facilities: {len(facilities)}")
        
        print("💳 Banking sample...")
        bank_customers, bank_transactions = generator.generate_banking_data(500, 2000)
        print(f"   Customers: {len(bank_customers)}, Transactions: {len(bank_transactions)}")
        
        print("👥 HR sample...")
        employees, exits = generator.generate_hr_data(300)
        print(f"   Employees: {len(employees)}, Exit Interviews: {len(exits)}")
        
        print("🕵️ Fraud sample...")
        users, fraud_tx = generator.generate_fraud_data(200, 1000)
        print(f"   Users: {len(users)}, Transactions: {len(fraud_tx)}")
        
        print("📈 Financial sample...")
        stocks, prices = generator.generate_financial_data(10, 30)
        print(f"   Stocks: {len(stocks)}, Price Records: {len(prices)}")
        
        print("🍽️ Restaurant sample...")
        restaurants, review_users, reviews = generator.generate_restaurant_data(50, 500, 200)
        print(f"   Restaurants: {len(restaurants)}, Users: {len(review_users)}, Reviews: {len(reviews)}")
        
        print("✅ Sample data generation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Sample data generation failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests
    if test_all_components():
        print("\n" + "=" * 60)
        # Generate sample data if tests pass
        generate_sample_data()
        
        print("\n🎯 Next Steps:")
        print("1. Run: python shared/scripts/database_setup.py --env development")
        print("2. Run: python setup_all_projects.py")
        print("3. Start with: jupyter lab ecommerce/notebooks/01_data_cleaning.ipynb")
    else:
        print("\n💡 Please fix the failing components before proceeding.")
        sys.exit(1)
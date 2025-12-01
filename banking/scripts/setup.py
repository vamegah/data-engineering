import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

from utils.data_generator import MockDataGenerator
from config.database import DatabaseConfig
import pandas as pd


def setup_banking_project():
    """Initialize banking project with sample data"""

    print("🚀 Setting up Banking Project...")
    print("📊 Bank Customer Churn Prediction - Customer retention and risk analysis")

    # Generate sample data
    generator = MockDataGenerator(seed=42)
    customers, transactions = generator.generate_banking_data()

    # Save to CSV
    customers.to_csv("../data/raw/banking_customers.csv", index=False)
    transactions.to_csv("../data/raw/banking_transactions.csv", index=False)

    print(f"✅ Generated: {len(customers)} customers, {len(transactions)} transactions")

    # Load to database (optional)
    try:
        engine = DatabaseConfig.get_engine()
        customers.to_sql("banking_customers", engine, if_exists="replace", index=False)
        transactions.to_sql(
            "banking_transactions", engine, if_exists="replace", index=False
        )
        print("✅ Data loaded to PostgreSQL database")
    except Exception as e:
        print(f"⚠️  Could not load to database: {e}")
        print(
            "💡 Make sure PostgreSQL is running and credentials are correct in shared/config/database.py"
        )

    print("✅ Banking project setup complete!")


if __name__ == "__main__":
    setup_banking_project()

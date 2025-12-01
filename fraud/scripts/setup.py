import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

from utils.data_generator import MockDataGenerator
from config.database import DatabaseConfig
import pandas as pd


def setup_fraud_project():
    """Initialize fraud detection project with sample data"""

    print("🚀 Setting up Fraud Detection Project...")
    print("📊 Fraud Detection - Anomaly detection and pattern recognition")

    # Generate sample data
    generator = MockDataGenerator(seed=42)
    users, transactions = generator.generate_fraud_data(
        n_transactions=50000, n_users=5000
    )

    # Save to CSV
    users.to_csv("../data/raw/fraud_users.csv", index=False)
    transactions.to_csv("../data/raw/fraud_transactions.csv", index=False)

    print(f"✅ Generated: {len(users)} users, {len(transactions)} transactions")
    print(f"✅ Fraud rate: {transactions['is_fraud'].mean():.2%}")

    # Load to database (optional)
    try:
        engine = DatabaseConfig.get_engine()
        users.to_sql("fraud_users", engine, if_exists="replace", index=False)
        transactions.to_sql(
            "fraud_transactions", engine, if_exists="replace", index=False
        )

        print("✅ Data loaded into database successfully!")
    except Exception as e:
        print(f"⚠️  Database loading skipped: {e}")

    print("✅ Fraud detection project setup complete!")


if __name__ == "__main__":
    setup_fraud_project()

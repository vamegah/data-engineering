import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config.database import DatabaseConfig
import logging

# Ensure logs directory exists before setting up logging
os.makedirs(os.path.join(os.path.dirname(__file__), "../../logs"), exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "../../logs/etl_pipeline.log")
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def run_fraud_etl():
    """ETL pipeline for fraud detection project"""

    logger.info("🔧 Starting Fraud Detection ETL Pipeline...")

    try:
        # 1. Extract - Load raw data
        logger.info("📥 Extracting data...")

        users = pd.read_csv("../data/raw/fraud_users.csv")
        transactions = pd.read_csv("../data/raw/fraud_transactions.csv")

        logger.info(f"Loaded {len(users)} users and {len(transactions)} transactions")

        # 2. Transform - Data cleaning and feature engineering
        logger.info("🔄 Transforming data...")

        # Clean users data
        users_clean = clean_users_data(users)

        # Clean transactions data
        transactions_clean = clean_transactions_data(transactions)

        # Create features
        fraud_data = create_features(users_clean, transactions_clean)

        # 3. Load - Save processed data
        logger.info("📤 Loading processed data...")

        # Save to processed directory
        users_clean.to_csv("../data/processed/fraud_users_clean.csv", index=False)
        transactions_clean.to_csv(
            "../data/processed/fraud_transactions_clean.csv", index=False
        )
        fraud_data.to_csv("../data/processed/fraud_data_clean.csv", index=False)
        # Load to database (optional)
        load_to_database(users_clean, transactions_clean, fraud_data)

        logger.info("✅ ETL pipeline completed successfully!")
        logger.info(f"Final dataset: {fraud_data.shape}")
        logger.info(f"Fraud rate: {fraud_data['is_fraud'].mean():.4f}")

    except Exception as e:
        logger.error(f"❌ ETL pipeline failed: {e}")
        raise


def clean_users_data(users_df):
    """Clean users data"""
    logger.info("🧹 Cleaning users data...")

    # Convert date columns
    users_df["signup_date"] = pd.to_datetime(users_df["signup_date"])

    # Handle missing values
    users_clean = users_df.dropna()

    # Remove duplicates
    users_clean = users_clean.drop_duplicates(subset=["user_id"])

    logger.info(f"Users after cleaning: {users_clean.shape}")
    return users_clean


def clean_transactions_data(transactions_df):
    """Clean transactions data"""
    logger.info("🧹 Cleaning transactions data...")

    # Convert date column
    transactions_df["transaction_date"] = pd.to_datetime(
        transactions_df["transaction_date"]
    )

    # Extract additional time features
    transactions_df["hour"] = transactions_df["transaction_date"].dt.hour
    transactions_df["day_of_week"] = transactions_df["transaction_date"].dt.day_name()
    transactions_df["month"] = transactions_df["transaction_date"].dt.month
    transactions_df["is_weekend"] = (
        transactions_df["transaction_date"].dt.dayofweek.isin([5, 6]).astype(int)
    )

    # Handle missing values
    transactions_clean = transactions_df.dropna()

    # Remove duplicates
    transactions_clean = transactions_clean.drop_duplicates(subset=["transaction_id"])

    # Remove negative amounts
    transactions_clean = transactions_clean[transactions_clean["amount"] > 0]

    logger.info(f"Transactions after cleaning: {transactions_clean.shape}")
    return transactions_clean


def create_features(users_clean, transactions_clean):
    """Create features for fraud detection"""
    logger.info("🎯 Creating features...")

    # Merge datasets
    fraud_data = transactions_clean.merge(users_clean, on="user_id", how="left")

    # User transaction statistics
    user_stats = (
        transactions_clean.groupby("user_id")
        .agg(
            {
                "amount": ["mean", "std", "max", "count"],
                "transaction_date": ["min", "max"],
            }
        )
        .reset_index()
    )

    user_stats.columns = [
        "user_id",
        "avg_amount",
        "std_amount",
        "max_amount",
        "transaction_count",
        "first_transaction",
        "last_transaction",
    ]

    # Calculate user behavior features
    user_stats["days_since_first_transaction"] = (
        pd.to_datetime("2024-01-01") - user_stats["first_transaction"]
    ).dt.days
    user_stats["transaction_frequency"] = user_stats["transaction_count"] / user_stats[
        "days_since_first_transaction"
    ].clip(lower=1)

    # Merge user stats
    fraud_data = fraud_data.merge(user_stats, on="user_id", how="left")

    # Create fraud-specific features
    fraud_data["amount_to_avg_ratio"] = fraud_data["amount"] / fraud_data["avg_amount"]
    fraud_data["is_high_value"] = (
        fraud_data["amount"] > fraud_data["amount"].quantile(0.95)
    ).astype(int)
    # Fix: Use 'hour' instead of 'hour_of_day' if present
    if "hour_of_day" in fraud_data.columns:
        fraud_data["is_late_night"] = (
            fraud_data["hour_of_day"].between(0, 5).astype(int)
        )
    elif "hour" in fraud_data.columns:
        fraud_data["is_late_night"] = fraud_data["hour"].between(0, 5).astype(int)
    else:
        fraud_data["is_late_night"] = 0

    # Fix: If 'location' column is missing, set is_international = 0
    if "location" in fraud_data.columns:
        fraud_data["is_international"] = (
            fraud_data["location"] == "International"
        ).astype(int)
    else:
        fraud_data["is_international"] = 0

    logger.info(f"Final feature set: {fraud_data.shape}")
    return fraud_data


def load_to_database(users_clean, transactions_clean, fraud_data):
    """Load data to database"""
    try:
        engine = DatabaseConfig.get_engine()

        # Load to database
        users_clean.to_sql(
            "fraud_users_clean", engine, if_exists="replace", index=False
        )
        transactions_clean.to_sql(
            "fraud_transactions_clean", engine, if_exists="replace", index=False
        )
        fraud_data.to_sql("fraud_data_clean", engine, if_exists="replace", index=False)

        logger.info("✅ Data loaded to database successfully!")
    except Exception as e:
        logger.warning(f"⚠️  Database loading skipped: {e}")


if __name__ == "__main__":
    # Setup plotting style
    import matplotlib.pyplot as plt

    try:
        plt.style.use("seaborn-v0_8")
    except Exception:
        plt.style.use("default")
    run_fraud_etl()

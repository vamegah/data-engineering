#!/usr/bin/env python3
"""
Banking ETL Pipeline
Extract, Transform, Load pipeline for banking customer data
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))
from config.database import DatabaseConfig
from utils.helpers import validate_data

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("../logs/etl_pipeline.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class BankingETL:
    def __init__(self):
        self.customers = None
        self.transactions = None
        self.processed_customers = None
        self.processed_transactions = None

    def extract_data(self, source_type="csv"):
        """Extract data from source"""
        logger.info("🔍 Extracting data from source...")

        try:
            if source_type == "csv":
                # Extract from CSV files
                self.customers = pd.read_csv("../data/raw/banking_customers.csv")
                self.transactions = pd.read_csv("../data/raw/banking_transactions.csv")

            elif source_type == "database":
                # Extract from database
                engine = DatabaseConfig.get_engine()
                self.customers = pd.read_sql("SELECT * FROM banking_customers", engine)
                self.transactions = pd.read_sql(
                    "SELECT * FROM banking_transactions", engine
                )

            logger.info(
                f"✅ Extracted {len(self.customers)} customers and {len(self.transactions)} transactions"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return False

    def transform_customers(self):
        """Transform and clean customers data"""
        logger.info("🔧 Transforming customers data...")

        try:
            df = self.customers.copy()

            # Data validation
            initial_count = len(df)
            validate_data(df, "Raw Customers Data")

            # Data cleaning
            df = df.drop_duplicates()
            df = df.dropna()

            # Data type conversions
            df["customer_id"] = df["customer_id"].astype(str)

            # Data validation rules
            df = df[df["age"] >= 18]  # Remove unrealistic ages
            df = df[df["balance"] >= 0]  # Remove negative balances
            df = df[df["credit_score"].between(300, 850)]  # Valid credit score range

            logger.info(
                f"✅ Customers transformation complete. Records: {initial_count} → {len(df)}"
            )
            self.processed_customers = df
            return True

        except Exception as e:
            logger.error(f"❌ Customers transformation failed: {e}")
            return False

    def transform_transactions(self):
        """Transform and clean transactions data"""
        logger.info("🔧 Transforming transactions data...")

        try:
            df = self.transactions.copy()

            # Data validation
            initial_count = len(df)
            validate_data(df, "Raw Transactions Data")

            # Data cleaning
            df = df.drop_duplicates()
            df = df.dropna()

            # Data type conversions
            df["transaction_id"] = df["transaction_id"].astype(str)
            df["customer_id"] = df["customer_id"].astype(str)
            df["date"] = pd.to_datetime(df["date"])

            # Remove transactions with invalid amounts
            df = df[df["amount"] != 0]

            # Adjust amounts based on transaction type
            df.loc[df["transaction_type"] == "Withdrawal", "amount"] = (
                df.loc[df["transaction_type"] == "Withdrawal", "amount"] * -1
            )
            df.loc[df["transaction_type"] == "Payment", "amount"] = (
                df.loc[df["transaction_type"] == "Payment", "amount"] * -1
            )

            logger.info(
                f"✅ Transactions transformation complete. Records: {initial_count} → {len(df)}"
            )
            self.processed_transactions = df
            return True

        except Exception as e:
            logger.error(f"❌ Transactions transformation failed: {e}")
            return False

    def create_features(self):
        """Create additional features for analysis"""
        logger.info("🔧 Creating additional features...")

        try:
            # Customer transaction aggregations
            customer_transactions = (
                self.processed_transactions.groupby("customer_id")
                .agg(
                    {
                        "amount": ["count", "mean", "std", "min", "max", "sum"],
                        "date": ["min", "max"],
                    }
                )
                .round(2)
            )

            # Flatten column names
            customer_transactions.columns = [
                "txn_count",
                "avg_amount",
                "std_amount",
                "min_amount",
                "max_amount",
                "total_amount",
                "first_txn",
                "last_txn",
            ]
            customer_transactions = customer_transactions.reset_index()

            # Calculate additional features
            customer_transactions["days_since_last_txn"] = (
                pd.to_datetime("2024-01-01") - customer_transactions["last_txn"]
            ).dt.days

            # Merge with customers data
            customers_enriched = self.processed_customers.merge(
                customer_transactions, on="customer_id", how="left"
            )

            # Fill NaN values for customers with no transactions
            fill_values = {
                "txn_count": 0,
                "avg_amount": 0,
                "std_amount": 0,
                "min_amount": 0,
                "max_amount": 0,
                "total_amount": 0,
                "days_since_last_txn": 365,
            }
            customers_enriched = customers_enriched.fillna(fill_values)

            # Create risk score feature
            customers_enriched["risk_score"] = (
                (customers_enriched["credit_score"] < 600).astype(int)
                + (customers_enriched["balance"] < 1000).astype(int)
                + (customers_enriched["active_member"] == 0).astype(int)
                + (customers_enriched["txn_count"] < 5).astype(int)
            )

            self.processed_customers = customers_enriched
            logger.info("✅ Feature engineering complete")
            return True

        except Exception as e:
            logger.error(f"❌ Feature engineering failed: {e}")
            return False

    def load_data(self, destination_type="both"):
        """Load processed data to destination"""
        logger.info("💾 Loading data to destination...")

        try:
            # Create processed directory if it doesn't exist
            os.makedirs("../data/processed", exist_ok=True)
            os.makedirs("../logs", exist_ok=True)

            if destination_type in ["csv", "both"]:
                # Save to CSV files
                self.processed_customers.to_csv(
                    "../data/processed/banking_customers_clean.csv", index=False
                )
                self.processed_transactions.to_csv(
                    "../data/processed/banking_transactions_clean.csv", index=False
                )
                logger.info("✅ Data saved to CSV files")

            if destination_type in ["database", "both"]:
                # Load to database
                engine = DatabaseConfig.get_engine()

                self.processed_customers.to_sql(
                    "banking_customers_clean", engine, if_exists="replace", index=False
                )
                self.processed_transactions.to_sql(
                    "banking_transactions_clean",
                    engine,
                    if_exists="replace",
                    index=False,
                )
                logger.info("✅ Data loaded to database")

            # Save processing metadata
            metadata = {
                "processing_date": datetime.now().isoformat(),
                "customers_processed": len(self.processed_customers),
                "transactions_processed": len(self.processed_transactions),
                "churn_rate": self.processed_customers["churn"].mean(),
                "total_balance": self.processed_customers["balance"].sum(),
            }

            metadata_df = pd.DataFrame([metadata])
            metadata_df.to_csv("../data/processed/processing_metadata.csv", index=False)

            logger.info("✅ Processing metadata saved")
            return True

        except Exception as e:
            logger.error(f"❌ Data loading failed: {e}")
            return False

    def run_quality_checks(self):
        """Run data quality checks"""
        logger.info("🔍 Running data quality checks...")

        checks = []

        # Check 1: Data completeness
        checks.append(
            {
                "check": "Data Completeness",
                "status": "PASS" if len(self.processed_customers) > 0 else "FAIL",
                "details": f"{len(self.processed_customers)} customers processed",
            }
        )

        # Check 2: No negative balances
        negative_balances = (self.processed_customers["balance"] < 0).sum()
        checks.append(
            {
                "check": "No Negative Balances",
                "status": "PASS" if negative_balances == 0 else "FAIL",
                "details": f"{negative_balances} negative balances found",
            }
        )

        # Check 3: Valid age range
        invalid_ages = (
            (self.processed_customers["age"] < 18)
            | (self.processed_customers["age"] > 100)
        ).sum()
        checks.append(
            {
                "check": "Valid Age Range",
                "status": "PASS" if invalid_ages == 0 else "FAIL",
                "details": f"{invalid_ages} invalid ages found",
            }
        )

        # Check 4: Churn rate within expected range
        churn_rate = self.processed_customers["churn"].mean()
        checks.append(
            {
                "check": "Reasonable Churn Rate",
                "status": "PASS" if 0.05 <= churn_rate <= 0.35 else "WARNING",
                "details": f"Churn rate: {churn_rate:.2%}",
            }
        )

        # Log results
        checks_df = pd.DataFrame(checks)
        for _, check in checks_df.iterrows():
            if check["status"] == "PASS":
                logger.info(f"✅ {check['check']}: {check['details']}")
            elif check["status"] == "WARNING":
                logger.warning(f"⚠️ {check['check']}: {check['details']}")
            else:
                logger.error(f"❌ {check['check']}: {check['details']}")

        checks_df.to_csv("../data/processed/quality_checks.csv", index=False)
        return checks_df


def run_etl_pipeline(source_type="csv", destination_type="both"):
    """Main ETL pipeline function"""
    logger.info("🏦 Banking ETL Pipeline Started")
    logger.info("=" * 50)

    start_time = datetime.now()
    etl = BankingETL()

    try:
        # Extract
        if not etl.extract_data(source_type):
            return False

        # Transform
        if not etl.transform_customers():
            return False

        if not etl.transform_transactions():
            return False

        # Feature engineering
        if not etl.create_features():
            return False

        # Quality checks
        quality_results = etl.run_quality_checks()

        # Load
        if not etl.load_data(destination_type):
            return False

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Summary
        logger.info("🎯 ETL PIPELINE SUMMARY")
        logger.info("=" * 30)
        logger.info(f"✅ Execution time: {duration:.2f} seconds")
        logger.info(f"✅ Customers processed: {len(etl.processed_customers):,}")
        logger.info(f"✅ Transactions processed: {len(etl.processed_transactions):,}")
        logger.info(f"✅ Churn rate: {etl.processed_customers['churn'].mean():.2%}")
        logger.info(
            f"✅ Total balance: ${etl.processed_customers['balance'].sum():,.2f}"
        )

        failed_checks = len(quality_results[quality_results["status"] == "FAIL"])
        if failed_checks == 0:
            logger.info("✅ All quality checks passed!")
        else:
            logger.warning(f"⚠️ {failed_checks} quality checks failed")

        return True

    except Exception as e:
        logger.error(f"❌ ETL pipeline failed: {e}")
        return False


if __name__ == "__main__":
    # Run the ETL pipeline
    success = run_etl_pipeline(source_type="csv", destination_type="csv")

    if success:
        logger.info("🎉 ETL Pipeline completed successfully!")
    else:
        logger.error("💥 ETL Pipeline failed!")
        sys.exit(1)

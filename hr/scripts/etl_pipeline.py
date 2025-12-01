#!/usr/bin/env python3
"""
HR Analytics ETL Pipeline
Automated data processing pipeline for HR attrition analysis
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
from utils.data_generator import MockDataGenerator
from utils.helpers import validate_data

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("../data/processed/etl_pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class HRETLPipeline:
    """ETL Pipeline for HR Analytics"""

    def __init__(self):
        self.data_generator = MockDataGenerator(seed=42)
        self.engine = None
        self.setup_database_connection()

    def setup_database_connection(self):
        """Setup database connection"""
        try:
            self.engine = DatabaseConfig.get_engine()
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
            self.engine = None

    def extract(self, use_sample_data=True):
        """Extract data from source"""
        logger.info("📥 Extracting HR data...")

        if use_sample_data:
            # Generate sample data
            employees, exit_interviews = self.data_generator.generate_hr_data()
            logger.info(
                f"✅ Generated sample data: {len(employees)} employees, {len(exit_interviews)} exit interviews"
            )
        else:
            # Load from actual source (CSV, database, API, etc.)
            try:
                employees = pd.read_csv("../data/raw/hr_employees.csv")
                exit_interviews = pd.read_csv("../data/raw/hr_exit_interviews.csv")
                logger.info(
                    f"✅ Loaded existing data: {len(employees)} employees, {len(exit_interviews)} exit interviews"
                )
            except FileNotFoundError:
                logger.warning("📝 No existing data found, using sample data")
                employees, exit_interviews = self.data_generator.generate_hr_data()

        return employees, exit_interviews

    def transform(self, employees, exit_interviews):
        """Transform and clean the data"""
        logger.info("🔧 Transforming HR data...")

        # Data validation
        logger.info("🔍 Validating data quality...")
        validate_data(employees, "Employees Raw Data")
        validate_data(exit_interviews, "Exit Interviews Raw Data")

        # Employees data transformation
        employees_clean = self.clean_employees_data(employees)

        # Exit interviews transformation
        exit_interviews_clean = self.clean_exit_interviews_data(exit_interviews)

        # Feature engineering
        employees_enriched = self.enrich_employees_data(employees_clean)

        logger.info(
            f"✅ Transformation complete: {len(employees_enriched)} employees, {len(exit_interviews_clean)} exit interviews"
        )

        return employees_enriched, exit_interviews_clean

    def clean_employees_data(self, df):
        """Clean employees data"""
        df_clean = df.copy()

        # Handle missing values
        initial_count = len(df_clean)
        df_clean = df_clean.dropna()
        logger.info(
            f"   Removed {initial_count - len(df_clean)} records with missing values"
        )

        # Remove duplicates
        duplicates = df_clean.duplicated().sum()
        df_clean = df_clean.drop_duplicates()
        logger.info(f"   Removed {duplicates} duplicate records")

        # Data type conversions
        df_clean["age"] = df_clean["age"].astype(int)
        df_clean["tenure"] = df_clean["tenure"].astype(int)
        df_clean["salary"] = df_clean["salary"].astype(float)
        df_clean["bonus"] = df_clean["bonus"].astype(float)

        # Handle outliers
        numeric_columns = ["salary", "bonus", "distance_from_home"]
        for col in numeric_columns:
            q1 = df_clean[col].quantile(0.01)
            q3 = df_clean[col].quantile(0.99)
            outliers = ((df_clean[col] < q1) | (df_clean[col] > q3)).sum()
            df_clean[col] = np.clip(df_clean[col], q1, q3)
            logger.info(f"   Capped {outliers} outliers in {col}")

        return df_clean

    def clean_exit_interviews_data(self, df):
        """Clean exit interviews data"""
        df_clean = df.copy()

        # Convert date column
        df_clean["exit_date"] = pd.to_datetime(df_clean["exit_date"])

        # Handle missing values
        initial_count = len(df_clean)
        df_clean = df_clean.dropna()
        logger.info(
            f"   Removed {initial_count - len(df_clean)} records with missing values from exit interviews"
        )

        return df_clean

    def enrich_employees_data(self, df):
        """Add derived features to employees data"""
        df_enriched = df.copy()

        # Create categorical features
        df_enriched["salary_category"] = pd.cut(
            df_enriched["salary"],
            bins=[0, 50000, 80000, 120000, np.inf],
            labels=["Low", "Medium", "High", "Very High"],
        )

        df_enriched["tenure_group"] = pd.cut(
            df_enriched["tenure"],
            bins=[0, 2, 5, 10, np.inf],
            labels=["0-2 years", "3-5 years", "6-10 years", "10+ years"],
        )

        df_enriched["age_group"] = pd.cut(
            df_enriched["age"],
            bins=[0, 25, 35, 45, 55, np.inf],
            labels=["18-25", "26-35", "36-45", "46-55", "55+"],
        )

        # Create risk flags
        df_enriched["high_risk_flag"] = (
            (df_enriched["job_satisfaction"] <= 2)
            | (df_enriched["overtime"] == "Yes")
            | (df_enriched["tenure"] < 2)
        ).astype(int)

        logger.info(
            "   Added derived features: salary_category, tenure_group, age_group, high_risk_flag"
        )

        return df_enriched

    def load(self, employees_clean, exit_interviews_clean):
        """Load data to destination"""
        logger.info("💾 Loading processed data...")

        # Save to processed CSV files
        employees_clean.to_csv("../data/processed/employees_clean.csv", index=False)
        exit_interviews_clean.to_csv(
            "../data/processed/exit_interviews_clean.csv", index=False
        )
        logger.info("✅ Data saved to processed CSV files")

        # Load to database if available
        if self.engine:
            try:
                employees_clean.to_sql(
                    "employees", self.engine, if_exists="replace", index=False
                )
                exit_interviews_clean.to_sql(
                    "exit_interviews", self.engine, if_exists="replace", index=False
                )
                logger.info("✅ Data loaded to database successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load data to database: {e}")
        else:
            logger.info("ℹ️  Database loading skipped (no connection)")

        # Generate data quality report
        self.generate_data_quality_report(employees_clean, exit_interviews_clean)

    def generate_data_quality_report(self, employees, exit_interviews):
        """Generate data quality report"""
        logger.info("📊 Generating data quality report...")

        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "employees_count": len(employees),
            "exit_interviews_count": len(exit_interviews),
            "attrition_rate": (employees["attrition"] == "Yes").mean() * 100,
            "data_quality_metrics": {
                "missing_values": employees.isnull().sum().sum()
                + exit_interviews.isnull().sum().sum(),
                "duplicate_records": employees.duplicated().sum()
                + exit_interviews.duplicated().sum(),
                "columns_processed": len(employees.columns)
                + len(exit_interviews.columns),
            },
        }

        # Save report
        report_df = pd.DataFrame([report])
        report_df.to_csv("../data/processed/data_quality_report.csv", index=False)
        logger.info("✅ Data quality report generated")

        return report

    def run_pipeline(self, use_sample_data=True):
        """Run the complete ETL pipeline"""
        logger.info("🚀 Starting HR Analytics ETL Pipeline")
        logger.info("=" * 50)

        start_time = datetime.now()

        try:
            # Extract
            employees_raw, exit_interviews_raw = self.extract(use_sample_data)

            # Transform
            employees_clean, exit_interviews_clean = self.transform(
                employees_raw, exit_interviews_raw
            )

            # Load
            self.load(employees_clean, exit_interviews_clean)

            end_time = datetime.now()
            duration = end_time - start_time

            logger.info(f"✅ ETL Pipeline completed successfully!")
            logger.info(f"⏱️  Duration: {duration.total_seconds():.2f} seconds")
            logger.info(
                f"📈 Processed {len(employees_clean)} employees and {len(exit_interviews_clean)} exit interviews"
            )

            return True

        except Exception as e:
            logger.error(f"❌ ETL Pipeline failed: {e}")
            return False


def main():
    """Main function to run the ETL pipeline"""
    pipeline = HRETLPipeline()

    # You can set use_sample_data=False to use existing CSV files
    success = pipeline.run_pipeline(use_sample_data=True)

    if success:
        print("\n🎉 ETL Pipeline completed successfully!")
        print("📁 Check the following files:")
        print("   - data/processed/employees_clean.csv")
        print("   - data/processed/exit_interviews_clean.csv")
        print("   - data/processed/data_quality_report.csv")
        print("   - data/processed/etl_pipeline.log")
    else:
        print("\n❌ ETL Pipeline failed. Check the log file for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

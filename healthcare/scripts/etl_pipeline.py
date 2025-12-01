import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

import pandas as pd
import numpy as np
from datetime import datetime
from config.database import DatabaseConfig
from utils.helpers import validate_data
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthcareETL:
    """ETL pipeline for Healthcare data"""

    def __init__(self):
        # Initialize a DatabaseConfig instance and get the engine
        # Previous code called the unbound method with `self`, which passed
        # the HealthcareETL instance into DatabaseConfig.get_engine and
        # caused attribute errors. Create a proper DatabaseConfig instance.
        try:
            db_conf = DatabaseConfig()
            self.engine = db_conf.get_engine()
        except Exception:
            # As a fallback, try the module-level convenience function if present
            try:
                from config.database import get_engine

                self.engine = get_engine()
            except Exception:
                # leave engine as None to allow higher-level error reporting
                self.engine = None

    def extract(self):
        """Extract data from source files"""
        logger.info("📥 Extracting healthcare data...")

        try:
            patients = pd.read_csv("../data/raw/healthcare_patients.csv")
            treatments = pd.read_csv("../data/raw/healthcare_treatments.csv")
            facilities = pd.read_csv("../data/raw/healthcare_facilities.csv")

            logger.info(
                f"✅ Extracted: {len(patients)} patients, {len(treatments)} treatments, {len(facilities)} facilities"
            )
            return patients, treatments, facilities

        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            raise

    def transform(self, patients, treatments, facilities):
        """Transform and clean the data"""
        logger.info("🔄 Transforming healthcare data...")

        # Clean patients data
        patients_clean = self.clean_patients(patients)

        # Clean treatments data
        treatments_clean = self.clean_treatments(treatments)

        # Clean facilities data
        facilities_clean = self.clean_facilities(facilities)

        # Data validation
        self.validate_data(patients_clean, treatments_clean, facilities_clean)

        logger.info("✅ Data transformation completed")
        return patients_clean, treatments_clean, facilities_clean

    def clean_patients(self, df):
        """Clean patients data"""
        df_clean = df.copy()

        # Convert dates
        df_clean["admission_date"] = pd.to_datetime(df_clean["admission_date"])
        df_clean["discharge_date"] = pd.to_datetime(df_clean["discharge_date"])

        # Fix date inconsistencies
        mask = df_clean["discharge_date"] < df_clean["admission_date"]
        df_clean.loc[mask, "discharge_date"] = df_clean.loc[
            mask, "admission_date"
        ] + pd.Timedelta(days=1)

        # Calculate length of stay
        df_clean["length_of_stay"] = (
            df_clean["discharge_date"] - df_clean["admission_date"]
        ).dt.days

        # Remove invalid records
        df_clean = df_clean[df_clean["length_of_stay"] >= 0]
        df_clean = df_clean[(df_clean["age"] >= 0) & (df_clean["age"] <= 120)]

        return df_clean

    def clean_treatments(self, df):
        """Clean treatments data"""
        df_clean = df.copy()

        # Convert date
        df_clean["treatment_date"] = pd.to_datetime(df_clean["treatment_date"])

        # Remove cost outliers using IQR
        Q1 = df_clean["cost"].quantile(0.25)
        Q3 = df_clean["cost"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        df_clean = df_clean[
            (df_clean["cost"] >= lower_bound) & (df_clean["cost"] <= upper_bound)
        ]
        df_clean = df_clean[df_clean["duration_days"] > 0]

        return df_clean

    def clean_facilities(self, df):
        """Clean facilities data"""
        df_clean = df.copy()

        # Basic validation
        df_clean = df_clean[df_clean["bed_capacity"] > 0]

        current_year = datetime.now().year
        df_clean = df_clean[
            (df_clean["established_year"] >= 1900)
            & (df_clean["established_year"] <= current_year)
        ]

        return df_clean

    def validate_data(self, patients, treatments, facilities):
        """Validate the cleaned data"""
        logger.info("🔍 Validating data quality...")

        # Check for required columns
        required_patient_cols = [
            "patient_id",
            "age",
            "admission_date",
            "discharge_date",
        ]
        required_treatment_cols = ["treatment_id", "patient_id", "cost"]
        required_facility_cols = ["facility_id", "facility_name", "bed_capacity"]

        for col in required_patient_cols:
            if col not in patients.columns:
                raise ValueError(f"Missing required column in patients: {col}")

        for col in required_treatment_cols:
            if col not in treatments.columns:
                raise ValueError(f"Missing required column in treatments: {col}")

        for col in required_facility_cols:
            if col not in facilities.columns:
                raise ValueError(f"Missing required column in facilities: {col}")

        # Check for data consistency
        if patients["length_of_stay"].min() < 0:
            raise ValueError("Invalid length of stay detected")

        if treatments["cost"].min() < 0:
            raise ValueError("Negative treatment costs detected")

    def load(self, patients, treatments, facilities):
        """Load data to database"""
        logger.info("📤 Loading data to database...")

        try:
            # Load to database
            patients.to_sql("patients", self.engine, if_exists="replace", index=False)
            treatments.to_sql(
                "treatments", self.engine, if_exists="replace", index=False
            )
            facilities.to_sql(
                "facilities", self.engine, if_exists="replace", index=False
            )

            logger.info("✅ Data loaded to database successfully")

        except Exception as e:
            logger.error(f"❌ Database loading failed: {e}")
            raise

    def run_pipeline(self):
        """Run the complete ETL pipeline"""
        logger.info("🚀 Starting Healthcare ETL Pipeline...")

        try:
            # Extract
            patients, treatments, facilities = self.extract()

            # Transform
            patients_clean, treatments_clean, facilities_clean = self.transform(
                patients, treatments, facilities
            )

            # Load
            self.load(patients_clean, treatments_clean, facilities_clean)

            # Save cleaned data to files
            patients_clean.to_csv("../data/processed/patients_clean.csv", index=False)
            treatments_clean.to_csv(
                "../data/processed/treatments_clean.csv", index=False
            )
            facilities_clean.to_csv(
                "../data/processed/facilities_clean.csv", index=False
            )

            logger.info("🎉 Healthcare ETL pipeline completed successfully!")

            # Return summary statistics
            return self.generate_summary(
                patients_clean, treatments_clean, facilities_clean
            )

        except Exception as e:
            logger.error(f"💥 ETL pipeline failed: {e}")
            raise

    def generate_summary(self, patients, treatments, facilities):
        """Generate pipeline summary"""
        summary = {
            "patients_processed": len(patients),
            "treatments_processed": len(treatments),
            "facilities_processed": len(facilities),
            "avg_patient_age": patients["age"].mean(),
            "readmission_rate": patients["readmission_30_days"].mean() * 100,
            "avg_treatment_cost": treatments["cost"].mean(),
            "pipeline_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        logger.info("📊 Pipeline Summary:")
        logger.info(f"  • Patients: {summary['patients_processed']}")
        logger.info(f"  • Treatments: {summary['treatments_processed']}")
        logger.info(f"  • Facilities: {summary['facilities_processed']}")
        logger.info(f"  • Avg Patient Age: {summary['avg_patient_age']:.1f}")
        logger.info(f"  • Readmission Rate: {summary['readmission_rate']:.1f}%")
        logger.info(f"  • Avg Treatment Cost: ${summary['avg_treatment_cost']:.2f}")

        return summary


def main():
    """Main function to run the ETL pipeline"""
    try:
        etl = HealthcareETL()
        summary = etl.run_pipeline()

        print("\n" + "=" * 50)
        print("🏥 HEALTHCARE ETL PIPELINE COMPLETE")
        print("=" * 50)
        for key, value in summary.items():
            if key != "pipeline_timestamp":
                print(f"  {key.replace('_', ' ').title()}: {value}")
        print(f"  Pipeline Timestamp: {summary['pipeline_timestamp']}")
        print("=" * 50)

    except Exception as e:
        print(f"❌ ETL Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

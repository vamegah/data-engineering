import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

from utils.data_generator import MockDataGenerator
from config.database import DatabaseConfig
import pandas as pd
import numpy as np


def setup_healthcare_project():
    """Initialize healthcare project with sample data"""

    print("🚀 Setting up Healthcare Patient Analytics Project...")
    print("📊 Analyzing patient outcomes and resource allocation")

    # Generate sample data
    generator = MockDataGenerator()
    patients, treatments, facilities = generator.generate_healthcare_data()

    # Save to CSV
    patients.to_csv("../data/raw/healthcare_patients.csv", index=False)
    treatments.to_csv("../data/raw/healthcare_treatments.csv", index=False)
    facilities.to_csv("../data/raw/healthcare_facilities.csv", index=False)

    print(
        f"✅ Generated: {len(patients)} patients, {len(treatments)} treatments, {len(facilities)} facilities"
    )

    # Load to database if configured
    try:
        engine = DatabaseConfig.get_engine()

        patients.to_sql("patients", engine, if_exists="replace", index=False)
        treatments.to_sql("treatments", engine, if_exists="replace", index=False)
        facilities.to_sql("facilities", engine, if_exists="replace", index=False)

        print("✅ Data loaded into database successfully!")
    except Exception as e:
        print(f"⚠️  Database loading skipped: {e}")
        print(
            "💡 Configure database in shared/config/database.py for full functionality"
        )

    # Create some basic analytics
    create_initial_analytics(patients, treatments, facilities)

    print("✅ Healthcare project setup complete!")


def create_initial_analytics(patients, treatments, facilities):
    """Create initial analytics and summary"""

    print("\n📈 Initial Analytics Summary:")
    print(f"• Average patient age: {patients['age'].mean():.1f} years")
    print(f"• Most common condition: {patients['primary_condition'].mode().iloc[0]}")
    print(f"• Readmission rate: {patients['readmission_30_days'].mean()*100:.1f}%")
    print(f"• Average treatment cost: ${treatments['cost'].mean():.2f}")
    print(f"• Number of facilities: {len(facilities)}")


if __name__ == "__main__":
    setup_healthcare_project()

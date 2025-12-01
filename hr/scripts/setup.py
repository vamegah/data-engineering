import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

from utils.data_generator import MockDataGenerator
from config.database import DatabaseConfig
import pandas as pd
import numpy as np


def setup_hr_project():
    """Initialize HR project with sample data"""

    print("🚀 Setting up HR Attrition Project...")
    print("📊 HR Analytics - Employee turnover and workforce analytics")

    # Generate sample data
    generator = MockDataGenerator(seed=42)
    employees, exit_interviews = generator.generate_hr_data()

    # Save to CSV
    employees.to_csv("../data/raw/hr_employees.csv", index=False)
    exit_interviews.to_csv("../data/raw/hr_exit_interviews.csv", index=False)

    print(
        f"✅ Generated: {len(employees)} employees, {len(exit_interviews)} exit interviews"
    )

    # Load to database (optional)
    try:
        engine = DatabaseConfig.get_engine()

        # Create tables
        with engine.connect() as conn:
            # Read and execute schema
            with open("../sql/schema_setup.sql", "r") as f:
                schema_sql = f.read()
                conn.execute(schema_sql)

            # Load data
            employees.to_sql("employees", engine, if_exists="replace", index=False)
            exit_interviews.to_sql(
                "exit_interviews", engine, if_exists="replace", index=False
            )

        print("✅ Data loaded to database successfully!")

    except Exception as e:
        print(f"⚠️  Database loading skipped: {e}")
        print("💡 You can configure database later in shared/config/database.py")

    print("✅ HR project setup complete!")


if __name__ == "__main__":
    setup_hr_project()

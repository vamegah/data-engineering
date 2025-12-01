#!/usr/bin/env python3
"""
Restaurant Data Setup Script
Generates mock restaurant review data for analysis
"""


import sys
import os
import pandas as pd

# Add project root to sys.path so 'shared' can be imported as a package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.utils.data_generator import MockDataGenerator
from shared.config.database import DatabaseConfig


def setup_restaurant_project():
    """Initialize restaurant project with sample data"""

    print("🍽️ Setting up Restaurant Review Analysis Project...")
    print("📊 Generating realistic restaurant and review data...")

    # Generate sample data
    generator = MockDataGenerator(seed=42)
    restaurants, users, reviews = generator.generate_restaurant_data(
        n_restaurants=200, n_reviews=10000, n_users=3000
    )

    # Save raw data
    raw_data_path = "../data/raw"
    os.makedirs(raw_data_path, exist_ok=True)

    restaurants.to_csv(f"{raw_data_path}/restaurant_restaurants.csv", index=False)
    users.to_csv(f"{raw_data_path}/restaurant_users.csv", index=False)
    reviews.to_csv(f"{raw_data_path}/restaurant_reviews.csv", index=False)

    print(f"✅ Generated: {len(restaurants)} restaurants")
    print(f"✅ Generated: {len(users)} users")
    print(f"✅ Generated: {len(reviews)} reviews")
    print(f"✅ Data saved to: {raw_data_path}/")

    # Display sample data
    print("\n📋 Sample Restaurant Data:")
    print(restaurants.head(3))
    print("\n📋 Sample Review Data:")
    print(reviews[["review_id", "restaurant_id", "rating", "review_text"]].head(3))

    print("\n🎉 Restaurant project setup complete!")
    print("\nNext: Run the ETL pipeline to process the data")


if __name__ == "__main__":
    setup_restaurant_project()

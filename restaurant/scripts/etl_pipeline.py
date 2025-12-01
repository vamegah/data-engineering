#!/usr/bin/env python3
"""
Restaurant ETL Pipeline
Data processing and transformation pipeline for restaurant reviews
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Add project root to sys.path so 'shared' can be imported as a package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.config.database import DatabaseConfig
from shared.utils.helpers import validate_data, VisualizationHelper


class RestaurantETL:
    def __init__(self):
        self.raw_data_path = "../data/raw"
        self.processed_data_path = "../data/processed"
        self.setup_directories()

    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.processed_data_path, exist_ok=True)
        os.makedirs(f"{self.processed_data_path}/cleaned", exist_ok=True)
        os.makedirs(f"{self.processed_data_path}/aggregated", exist_ok=True)

    def load_raw_data(self):
        """Load raw CSV files"""
        print("📥 Loading raw data...")

        try:
            self.restaurants = pd.read_csv(
                f"{self.raw_data_path}/restaurant_restaurants.csv"
            )
            self.users = pd.read_csv(f"{self.raw_data_path}/restaurant_users.csv")
            self.reviews = pd.read_csv(f"{self.raw_data_path}/restaurant_reviews.csv")

            print(f"✅ Loaded {len(self.restaurants)} restaurants")
            print(f"✅ Loaded {len(self.users)} users")
            print(f"✅ Loaded {len(self.reviews)} reviews")

        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            print("💡 Run setup.py first to generate sample data")
            raise

    def clean_restaurants_data(self):
        """Clean and validate restaurants data"""
        print("🧹 Cleaning restaurants data...")

        # Create a copy
        df = self.restaurants.copy()

        # Basic validation
        validate_data(df, "Raw Restaurants")

        # Handle missing values
        df["cuisine_type"] = df["cuisine_type"].fillna("Other")
        df["price_range"] = df["price_range"].fillna("$$")
        df["location"] = df["location"].fillna("Unknown")

        # Ensure numeric fields are valid
        df["avg_rating"] = pd.to_numeric(df["avg_rating"], errors="coerce").fillna(3.0)
        df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").fillna(
            0
        )
        df["opening_year"] = pd.to_numeric(df["opening_year"], errors="coerce")

        # Calculate restaurant age
        current_year = datetime.now().year
        df["restaurant_age"] = current_year - df["opening_year"]
        df["restaurant_age"] = df["restaurant_age"].clip(lower=0)  # No negative ages

        # Categorize restaurants by popularity
        df["popularity_tier"] = pd.cut(
            df["review_count"],
            bins=[0, 10, 50, 200, float("inf")],
            labels=["New", "Growing", "Popular", "Very Popular"],
        )

        # Categorize by rating
        df["rating_tier"] = pd.cut(
            df["avg_rating"],
            bins=[0, 2, 3, 4, 4.5, 5],
            labels=["Poor", "Average", "Good", "Very Good", "Excellent"],
        )

        self.restaurants_clean = df
        print(f"✅ Cleaned restaurants data: {len(df)} records")

    def clean_users_data(self):
        """Clean and validate users data"""
        print("🧹 Cleaning users data...")

        df = self.users.copy()
        validate_data(df, "Raw Users")

        # Handle missing values
        df["location"] = df["location"].fillna("Unknown")
        df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").fillna(
            0
        )

        # Convert date
        df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")

        # Calculate user tenure (days since joining)
        df["user_tenure_days"] = (datetime.now() - df["join_date"]).dt.days
        df["user_tenure_days"] = df["user_tenure_days"].fillna(0).clip(lower=0)

        # Categorize users by activity level
        df["user_activity"] = pd.cut(
            df["review_count"],
            bins=[0, 1, 5, 20, float("inf")],
            labels=["Inactive", "Casual", "Active", "Super Reviewer"],
        )

        self.users_clean = df
        print(f"✅ Cleaned users data: {len(df)} records")

    def clean_reviews_data(self):
        """Clean and validate reviews data"""
        print("🧹 Cleaning reviews data...")

        df = self.reviews.copy()
        validate_data(df, "Raw Reviews")

        # Handle missing values
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(3.0)
        df["service_rating"] = pd.to_numeric(
            df["service_rating"], errors="coerce"
        ).fillna(3)
        df["food_rating"] = pd.to_numeric(df["food_rating"], errors="coerce").fillna(3)
        df["ambiance_rating"] = pd.to_numeric(
            df["ambiance_rating"], errors="coerce"
        ).fillna(3)
        df["useful_count"] = pd.to_numeric(df["useful_count"], errors="coerce").fillna(
            0
        )

        # Convert date
        df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")

        # Extract review length
        df["review_length"] = df["review_text"].str.len().fillna(0)

        # Categorize review sentiment based on rating
        df["sentiment"] = pd.cut(
            df["rating"],
            bins=[0, 2, 3.5, 4.5, 5],
            labels=["Negative", "Neutral", "Positive", "Very Positive"],
        )

        # Calculate overall satisfaction score (weighted average)
        df["overall_satisfaction"] = (
            df["rating"] * 0.4
            + df["food_rating"] * 0.3
            + df["service_rating"] * 0.2
            + df["ambiance_rating"] * 0.1
        )

        self.reviews_clean = df
        print(f"✅ Cleaned reviews data: {len(df)} records")

    def create_aggregated_datasets(self):
        """Create aggregated datasets for analysis"""
        print("📊 Creating aggregated datasets...")

        # Merge data for comprehensive analysis
        merged_data = self.reviews_clean.merge(
            self.restaurants_clean,
            on="restaurant_id",
            suffixes=("_review", "_restaurant"),
        ).merge(self.users_clean, on="user_id")

        # Restaurant-level aggregations
        restaurant_agg = (
            merged_data.groupby("restaurant_id")
            .agg(
                {
                    "rating": ["count", "mean", "std"],
                    "service_rating": "mean",
                    "food_rating": "mean",
                    "ambiance_rating": "mean",
                    "review_length": "mean",
                    "useful_count": "sum",
                    "sentiment": lambda x: (x == "Positive").mean(),
                }
            )
            .round(3)
        )

        restaurant_agg.columns = [
            "_".join(col).strip() for col in restaurant_agg.columns
        ]
        restaurant_agg = restaurant_agg.rename(
            columns={
                "rating_count": "total_reviews",
                "rating_mean": "avg_rating",
                "rating_std": "rating_std",
                "service_rating_mean": "avg_service_rating",
                "food_rating_mean": "avg_food_rating",
                "ambiance_rating_mean": "avg_ambiance_rating",
                "review_length_mean": "avg_review_length",
                "useful_count_sum": "total_useful_votes",
                "sentiment_<lambda>": "positive_sentiment_ratio",
            }
        )

        # Add restaurant details
        restaurant_agg = restaurant_agg.merge(
            self.restaurants_clean[
                ["restaurant_id", "name", "cuisine_type", "price_range", "location"]
            ],
            on="restaurant_id",
        )

        # Cuisine-level aggregations - FIXED to match EDA notebook expectations
        cuisine_agg = (
            merged_data.groupby("cuisine_type")
            .agg(
                {
                    "rating": ["count", "mean"],
                    "restaurant_id": "nunique",
                }
            )
            .round(3)
        )

        cuisine_agg.columns = ["_".join(col).strip() for col in cuisine_agg.columns]
        cuisine_agg = cuisine_agg.rename(
            columns={
                "rating_count": "total_reviews",
                "rating_mean": "avg_rating",
                "restaurant_id_nunique": "unique_restaurants",
            }
        )

        # Reset index to make cuisine_type a column and reorder columns
        cuisine_agg = cuisine_agg.reset_index()
        cuisine_agg = cuisine_agg[
            ["cuisine_type", "avg_rating", "total_reviews", "unique_restaurants"]
        ]

        # Time-based aggregations (monthly trends)
        merged_data["review_month"] = merged_data["review_date"].dt.to_period("M")
        monthly_trends = (
            merged_data.groupby("review_month")
            .agg({"review_id": "count", "rating": "mean", "useful_count": "mean"})
            .reset_index()
        )
        monthly_trends["review_month"] = monthly_trends["review_month"].astype(str)
        monthly_trends = monthly_trends.rename(columns={"review_id": "review_count"})

        self.restaurant_aggregated = restaurant_agg
        self.cuisine_aggregated = cuisine_agg
        self.monthly_trends = monthly_trends

        print(f"✅ Created restaurant aggregations: {len(restaurant_agg)} restaurants")
        print(f"✅ Created cuisine aggregations: {len(cuisine_agg)} cuisines")
        print(f"✅ Created monthly trends: {len(monthly_trends)} months")

        # Display column information for verification
        print(f"\n📋 Column verification:")
        print(f"   cuisine_aggregated columns: {list(cuisine_agg.columns)}")
        print(
            f"   Expected columns: ['cuisine_type', 'avg_rating', 'total_reviews', 'unique_restaurants']"
        )

    def save_processed_data(self):
        """Save all processed data to files"""
        print("💾 Saving processed data...")

        # Save cleaned data
        self.restaurants_clean.to_csv(
            f"{self.processed_data_path}/cleaned/restaurants_clean.csv", index=False
        )
        self.users_clean.to_csv(
            f"{self.processed_data_path}/cleaned/users_clean.csv", index=False
        )
        self.reviews_clean.to_csv(
            f"{self.processed_data_path}/cleaned/reviews_clean.csv", index=False
        )

        # Save aggregated data
        self.restaurant_aggregated.to_csv(
            f"{self.processed_data_path}/aggregated/restaurant_aggregated.csv",
            index=False,
        )
        self.cuisine_aggregated.to_csv(
            f"{self.processed_data_path}/aggregated/cuisine_aggregated.csv", index=False
        )
        self.monthly_trends.to_csv(
            f"{self.processed_data_path}/aggregated/monthly_trends.csv", index=False
        )

        print("✅ All processed data saved successfully!")

    def load_to_database(self):
        """Load processed data to PostgreSQL database"""
        print("🗄️ Loading data to database...")

        try:
            engine = DatabaseConfig.get_engine()

            # Load cleaned data to database
            self.restaurants_clean.to_sql(
                "restaurants", engine, if_exists="replace", index=False
            )
            self.users_clean.to_sql("users", engine, if_exists="replace", index=False)
            self.reviews_clean.to_sql(
                "reviews", engine, if_exists="replace", index=False
            )

            print("✅ Data loaded to database successfully!")

        except Exception as e:
            print(f"⚠️  Database loading skipped: {e}")
            print(
                "💡 Make sure PostgreSQL is running and configured in shared/config/database.py"
            )

    def run_pipeline(self):
        """Execute the complete ETL pipeline"""
        print("🔧 Starting Restaurant ETL Pipeline...")
        print("=" * 50)

        try:
            self.load_raw_data()
            self.clean_restaurants_data()
            self.clean_users_data()
            self.clean_reviews_data()
            self.create_aggregated_datasets()
            self.save_processed_data()
            self.load_to_database()

            print("\n🎉 ETL pipeline completed successfully!")
            print("\n📊 Data Summary:")
            print(f"   Restaurants: {len(self.restaurants_clean)}")
            print(f"   Users: {len(self.users_clean)}")
            print(f"   Reviews: {len(self.reviews_clean)}")
            print(
                f"   Cuisine Types: {self.restaurants_clean['cuisine_type'].nunique()}"
            )
            print(
                f"   Date Range: {self.reviews_clean['review_date'].min()} to {self.reviews_clean['review_date'].max()}"
            )

        except Exception as e:
            print(f"❌ ETL pipeline failed: {e}")
            raise


def main():
    """Main function to run the ETL pipeline"""
    etl = RestaurantETL()
    etl.run_pipeline()


if __name__ == "__main__":
    main()

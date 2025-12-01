# Ensure local 'shared' module is found
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "/data-engineering-portfolio/shared",
    )
)

from shared.utils.data_generator import MockDataGenerator
from shared.config.database import DatabaseConfig
import pandas as pd
import numpy as np


def setup_ecommerce_project():
    """Initialize e-commerce project with sample data"""

    print("🚀 Setting up E-commerce Project...")
    print("📊 E-commerce Sales Analysis - Customer behavior and sales optimization")

    # Generate sample data
    generator = MockDataGenerator(seed=42)
    customers, products, transactions = generator.generate_ecommerce_data(
        n_customers=5000, n_products=200, n_transactions=50000
    )

    # Ensure raw data directory exists
    os.makedirs("../data/raw", exist_ok=True)

    # Diagnostic: print products columns
    print("Products columns:", products.columns.tolist())

    # Save to CSV
    customers.to_csv("../data/raw/ecommerce_customers.csv", index=False)
    products.to_csv("../data/raw/ecommerce_products.csv", index=False)
    transactions.to_csv("../data/raw/ecommerce_transactions.csv", index=False)

    print(
        f"✅ Generated: {len(customers)} customers, {len(products)} products, {len(transactions)} transactions"
    )

    # Create database tables and load data
    try:
        engine = DatabaseConfig.get_engine()

        # Load to database
        customers.to_sql("customers", engine, if_exists="replace", index=False)
        products.to_sql("products", engine, if_exists="replace", index=False)
        transactions.to_sql("transactions", engine, if_exists="replace", index=False)

        print("✅ Data loaded into PostgreSQL database")
    except Exception as e:
        print(f"⚠️  Database loading skipped: {e}")
        print(
            "💡 Make sure PostgreSQL is running and credentials are correct in shared/config/database.py"
        )

    # Create some basic processed data
    create_processed_data(customers, products, transactions)

    print("✅ E-commerce project setup complete!")


def create_processed_data(customers, products, transactions):
    """Create initial processed datasets"""

    # Merge transactions with customer and product data

    # Use correct price column if 'price' is missing
    price_col = "price"
    if price_col not in products.columns:
        # Try common alternatives
        for alt in ["unit_price", "product_price", "sale_price"]:
            if alt in products.columns:
                price_col = alt
                break
    print(f"Using price column: {price_col}")

    enriched_transactions = transactions.merge(
        customers[["customer_id", "location", "tier"]], on="customer_id", how="left"
    ).merge(
        products[["product_id", "product_name", "category", price_col]],
        on="product_id",
        how="left",
    )

    # Diagnostic: print columns after merge
    print("enriched_transactions columns:", enriched_transactions.columns.tolist())

    # Find correct price column after merge
    merged_price_col = price_col
    if price_col not in enriched_transactions.columns:
        # Try common merge suffixes
        for alt in [f"{price_col}_x", f"{price_col}_y"]:
            if alt in enriched_transactions.columns:
                merged_price_col = alt
                break
    print(f"Using merged price column: {merged_price_col}")

    # Calculate revenue
    enriched_transactions["revenue"] = (
        enriched_transactions["quantity"] * enriched_transactions[merged_price_col]
    )

    # Ensure processed data directory exists
    os.makedirs("../data/processed", exist_ok=True)

    # Save enriched data
    enriched_transactions.to_csv(
        "../data/processed/enriched_transactions.csv", index=False
    )

    # Create customer summary
    customer_summary = (
        enriched_transactions.groupby("customer_id")
        .agg({"revenue": "sum", "transaction_id": "count", "date": ["min", "max"]})
        .round(2)
    )

    customer_summary.columns = [
        "total_spent",
        "transaction_count",
        "first_purchase",
        "last_purchase",
    ]
    customer_summary = customer_summary.reset_index()

    customer_summary.to_csv("../data/processed/customer_summary.csv", index=False)

    print("✅ Created processed datasets")


if __name__ == "__main__":
    setup_ecommerce_project()

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

import pandas as pd
import numpy as np
from datetime import datetime
from shared.config.database import DatabaseConfig
from shared.utils.helpers import validate_data


def run_ecommerce_etl():
    """Complete ETL pipeline for e-commerce data"""

    print("🔧 Starting E-commerce ETL Pipeline...")
    print("=" * 50)

    # Extract: Load raw data
    print("📥 Step 1: Extracting raw data...")

    try:
        customers = pd.read_csv("../data/raw/ecommerce_customers.csv")
        products = pd.read_csv("../data/raw/ecommerce_products.csv")
        transactions = pd.read_csv("../data/raw/ecommerce_transactions.csv")

        print(
            f"✅ Loaded: {len(customers)} customers, {len(products)} products, {len(transactions)} transactions"
        )
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    # Transform: Data cleaning and processing
    print("\\n🔄 Step 2: Transforming data...")

    # Data type conversions
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])
    transactions["date"] = pd.to_datetime(transactions["date"])

    # Handle missing values
    customers_clean = customers.dropna()
    products_clean = products.fillna(
        {"category": "Unknown", "price": products["price"].median()}
    )
    transactions_clean = transactions.dropna()

    # Remove duplicates
    customers_clean = customers_clean.drop_duplicates()
    products_clean = products_clean.drop_duplicates()
    transactions_clean = transactions_clean.drop_duplicates()

    # Feature engineering
    latest_date = transactions_clean["date"].max()
    customers_clean["tenure_days"] = (
        latest_date - customers_clean["signup_date"]
    ).dt.days

    products_clean["price_segment"] = pd.cut(
        products_clean["price"],
        bins=[0, 50, 100, 200, 500],
        labels=["Budget", "Mid-range", "Premium", "Luxury"],
    )
    products_clean["profit_margin"] = (
        (products_clean["price"] - products_clean["cost"]) / products_clean["price"]
    ) * 100

    # Create enriched transactions
    enriched_transactions = transactions_clean.merge(
        customers_clean[["customer_id", "location", "tier", "tenure_days"]],
        on="customer_id",
        how="left",
    ).merge(
        products_clean[
            [
                "product_id",
                "product_name",
                "category",
                "price",
                "price_segment",
                "profit_margin",
            ]
        ],
        on="product_id",
        how="left",
    )

    enriched_transactions["revenue"] = (
        enriched_transactions["quantity"] * enriched_transactions["price"]
    )
    enriched_transactions["profit"] = enriched_transactions["quantity"] * (
        enriched_transactions["price"] * (enriched_transactions["profit_margin"] / 100)
    )
    enriched_transactions["month"] = enriched_transactions["date"].dt.to_period("M")

    print("✅ Data transformation completed")

    # Load: Save processed data
    print("\\n📤 Step 3: Loading processed data...")

    # Save to processed directory
    customers_clean.to_csv("../data/processed/customers_clean.csv", index=False)
    products_clean.to_csv("../data/processed/products_clean.csv", index=False)
    enriched_transactions.to_csv(
        "../data/processed/enriched_transactions.csv", index=False
    )

    # Create business summaries
    create_business_summaries(enriched_transactions, customers_clean, products_clean)

    # Load to database (optional)
    try:
        load_to_database(customers_clean, products_clean, enriched_transactions)
    except Exception as e:
        print(f"⚠️  Database loading skipped: {e}")

    print("\\n✅ ETL pipeline completed successfully!")

    # Print summary statistics
    print_summary_statistics(enriched_transactions, customers_clean, products_clean)


def create_business_summaries(transactions, customers, products):
    """Create business summary datasets"""

    # Customer summary
    customer_summary = (
        transactions.groupby("customer_id")
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
    customer_summary = customer_summary.merge(
        customers[["customer_id", "location", "tier"]], on="customer_id"
    )
    customer_summary["avg_order_value"] = (
        customer_summary["total_spent"] / customer_summary["transaction_count"]
    )

    customer_summary.to_csv("../data/processed/customer_summary.csv", index=False)

    # Product performance
    product_performance = (
        transactions.groupby(["product_id", "product_name", "category"])
        .agg({"quantity": "sum", "revenue": "sum", "transaction_id": "count"})
        .round(2)
    )

    product_performance.columns = [
        "total_quantity",
        "total_revenue",
        "transaction_count",
    ]
    product_performance = product_performance.reset_index()
    product_performance = product_performance.merge(
        products[["product_id", "price", "profit_margin"]], on="product_id"
    )
    product_performance["avg_sale_price"] = (
        product_performance["total_revenue"] / product_performance["total_quantity"]
    )

    product_performance.to_csv("../data/processed/product_performance.csv", index=False)

    # Monthly sales
    monthly_sales = (
        transactions.groupby("month")
        .agg(
            {
                "revenue": "sum",
                "profit": "sum",
                "transaction_id": "count",
                "customer_id": "nunique",
            }
        )
        .round(2)
    )

    monthly_sales.columns = [
        "monthly_revenue",
        "monthly_profit",
        "transaction_count",
        "unique_customers",
    ]
    monthly_sales = monthly_sales.reset_index()
    monthly_sales["avg_transaction_value"] = (
        monthly_sales["monthly_revenue"] / monthly_sales["transaction_count"]
    )

    monthly_sales.to_csv("../data/processed/monthly_sales.csv", index=False)

    print("✅ Business summaries created")


def load_to_database(customers, products, transactions):
    """Load data to PostgreSQL database"""

    engine = DatabaseConfig.get_engine()

    # Load to database
    customers.to_sql("customers", engine, if_exists="replace", index=False)
    products.to_sql("products", engine, if_exists="replace", index=False)
    transactions.to_sql("transactions", engine, if_exists="replace", index=False)

    print("✅ Data loaded to PostgreSQL database")


def print_summary_statistics(transactions, customers, products):
    """Print summary statistics"""

    print("\\n📊 ETL Summary Statistics:")
    print("=" * 40)
    print(f"Total Customers: {len(customers):,}")
    print(f"Total Products: {len(products):,}")
    print(f"Total Transactions: {len(transactions):,}")
    print(f"Total Revenue: ${transactions['revenue'].sum():,.2f}")
    print(f"Total Profit: ${transactions['profit'].sum():,.2f}")
    print(
        f"Date Range: {transactions['date'].min().strftime('%Y-%m-%d')} to {transactions['date'].max().strftime('%Y-%m-%d')}"
    )
    print(f"Average Transaction Value: ${transactions['revenue'].mean():.2f}")
    print(
        f"Most Popular Category: {transactions['category'].mode().iloc[0] if not transactions['category'].mode().empty else 'N/A'}"
    )


if __name__ == "__main__":
    run_ecommerce_etl()

#!/usr/bin/env python3
"""
Financial Stock Analysis - Project Setup
Generates mock stock market data for analysis
"""


import sys
import os

# Add project root to sys.path so 'shared' can be imported as a package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.utils.data_generator import MockDataGenerator
from shared.config.database import DatabaseConfig
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def setup_financial_project():
    """Initialize financial project with sample stock data"""

    print("🚀 Setting up Financial Stock Analysis Project...")
    print("📊 Generating realistic stock market data...")

    # Generate sample data
    generator = MockDataGenerator(seed=42)
    stocks, stock_prices = generator.generate_financial_data()

    # Save to CSV files
    stocks.to_csv("../data/raw/financial_stocks.csv", index=False)
    stock_prices.to_csv("../data/raw/financial_prices.csv", index=False)

    print(f"✅ Generated: {len(stocks)} stocks, {len(stock_prices)} price records")
    print("📈 Sample stocks:")
    print(stocks[["symbol", "company_name", "sector", "market_cap"]].head())

    # Load to database if configured
    try:
        engine = DatabaseConfig.get_engine()

        # Create tables
        with engine.connect() as conn:
            # Create stocks table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stocks (
                    stock_id VARCHAR(50) PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    company_name VARCHAR(200),
                    sector VARCHAR(100),
                    market_cap VARCHAR(50),
                    dividend_yield DECIMAL(10,4)
                )
            """
            )

            # Create stock_prices table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id SERIAL PRIMARY KEY,
                    stock_id VARCHAR(50) REFERENCES stocks(stock_id),
                    date DATE NOT NULL,
                    open DECIMAL(10,2),
                    high DECIMAL(10,2),
                    low DECIMAL(10,2),
                    close DECIMAL(10,2),
                    volume BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

        # Load data
        stocks.to_sql("stocks", engine, if_exists="replace", index=False)
        stock_prices.to_sql("stock_prices", engine, if_exists="replace", index=False)

        print("✅ Data loaded to PostgreSQL database")

    except Exception as e:
        print(f"⚠️  Database loading skipped: {e}")
        print(
            "💡 Make sure PostgreSQL is running and credentials are configured in shared/config/database.py"
        )

    print("✅ Financial project setup complete!")


if __name__ == "__main__":
    setup_financial_project()

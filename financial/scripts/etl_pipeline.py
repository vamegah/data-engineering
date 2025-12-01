#!/usr/bin/env python3
"""
Financial Stock Analysis - ETL Pipeline
Data processing and transformation pipeline for stock data
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from shared.config.database import get_engine
from shared.utils.helpers import validate_data, VisualizationHelper
import warnings

warnings.filterwarnings("ignore")


class FinancialETL:
    def __init__(self):
        self.engine = get_engine()
        VisualizationHelper.setup_plotting()

    def extract_data(self):
        """Extract data from CSV files or database"""
        print("📥 Extracting financial data...")

        try:
            # Try to load from database first
            stocks = pd.read_sql("SELECT * FROM stocks", self.engine)
            stock_prices = pd.read_sql("SELECT * FROM stock_prices", self.engine)
            print("✅ Data loaded from database")
        except:
            # Fall back to CSV files
            stocks = pd.read_csv("../data/raw/financial_stocks.csv")
            stock_prices = pd.read_csv("../data/raw/financial_prices.csv")
            print("✅ Data loaded from CSV files")

        return stocks, stock_prices

    def transform_data(self, stocks, stock_prices):
        """Clean and transform the financial data"""
        print("🔄 Transforming financial data...")

        # Data validation
        validate_data(stocks, "Stocks Data")
        validate_data(stock_prices, "Stock Prices Data")

        # Data cleaning
        stocks_clean = stocks.copy()
        prices_clean = stock_prices.copy()

        # Handle missing values
        stocks_clean = stocks_clean.dropna(subset=["symbol", "company_name"])
        prices_clean = prices_clean.dropna(subset=["stock_id", "date", "close"])

        # Ensure correct data types
        prices_clean["date"] = pd.to_datetime(prices_clean["date"])
        prices_clean["close"] = pd.to_numeric(prices_clean["close"], errors="coerce")
        prices_clean["volume"] = pd.to_numeric(prices_clean["volume"], errors="coerce")

        # Remove duplicates
        prices_clean = prices_clean.drop_duplicates(subset=["stock_id", "date"])

        # Calculate additional features
        prices_clean = self.calculate_technical_indicators(prices_clean)

        print(
            f"✅ Transformed: {len(stocks_clean)} stocks, {len(prices_clean)} price records"
        )
        return stocks_clean, prices_clean

    def calculate_technical_indicators(self, prices_df):
        """Calculate technical indicators for stock analysis"""
        print("📈 Calculating technical indicators...")

        # Sort by stock and date
        prices_df = prices_df.sort_values(["stock_id", "date"])

        # Calculate daily returns
        prices_df["daily_return"] = prices_df.groupby("stock_id")["close"].pct_change()

        # Calculate moving averages
        prices_df["sma_20"] = prices_df.groupby("stock_id")["close"].transform(
            lambda x: x.rolling(window=20, min_periods=1).mean()
        )
        prices_df["sma_50"] = prices_df.groupby("stock_id")["close"].transform(
            lambda x: x.rolling(window=50, min_periods=1).mean()
        )

        # Calculate volatility (standard deviation of returns)
        prices_df["volatility_20"] = prices_df.groupby("stock_id")[
            "daily_return"
        ].transform(lambda x: x.rolling(window=20, min_periods=1).std())

        # Calculate RSI (Relative Strength Index)
        def calculate_rsi(series, window=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        prices_df["rsi_14"] = prices_df.groupby("stock_id")["close"].transform(
            lambda x: calculate_rsi(x, 14)
        )

        # Calculate Bollinger Bands
        prices_df["bb_upper"] = prices_df.groupby("stock_id")["close"].transform(
            lambda x: x.rolling(window=20).mean() + (x.rolling(window=20).std() * 2)
        )
        prices_df["bb_lower"] = prices_df.groupby("stock_id")["close"].transform(
            lambda x: x.rolling(window=20).mean() - (x.rolling(window=20).std() * 2)
        )

        return prices_df

    def load_data(self, stocks_clean, prices_clean):
        """Load processed data to database"""
        print("💾 Loading processed data...")

        try:
            # Save to processed CSV files
            stocks_clean.to_csv("../data/processed/stocks_processed.csv", index=False)
            prices_clean.to_csv("../data/processed/prices_processed.csv", index=False)

            # Update database with processed data
            stocks_clean.to_sql(
                "stocks_processed", self.engine, if_exists="replace", index=False
            )
            prices_clean.to_sql(
                "stock_prices_processed", self.engine, if_exists="replace", index=False
            )

            print("✅ Processed data saved to files and database")

        except Exception as e:
            print(f"⚠️  Database save failed: {e}")
            print("✅ Processed data saved to CSV files only")

    def generate_analytics(self, stocks_clean, prices_clean):
        """Generate analytical datasets and reports"""
        print("📊 Generating analytics...")

        # Sector performance analysis
        sector_performance = prices_clean.merge(stocks_clean, on="stock_id")
        sector_performance = (
            sector_performance.groupby(["sector", "date"])
            .agg(
                {
                    "close": ["mean", "std", "min", "max"],
                    "volume": "sum",
                    "daily_return": "std",  # as volatility
                }
            )
            .round(2)
        )

        sector_performance.columns = [
            "avg_price",
            "price_std",
            "min_price",
            "max_price",
            "total_volume",
            "volatility",
        ]
        sector_performance = sector_performance.reset_index()

        # Save analytics
        sector_performance.to_csv(
            "../data/processed/sector_performance.csv", index=False
        )

        print("✅ Analytics datasets generated")
        return sector_performance

    def run_pipeline(self):
        """Execute the complete ETL pipeline"""
        print("🚀 Starting Financial ETL Pipeline...")
        print("=" * 50)

        # Extract
        stocks, stock_prices = self.extract_data()

        # Transform
        stocks_clean, prices_clean = self.transform_data(stocks, stock_prices)

        # Generate Analytics
        analytics = self.generate_analytics(stocks_clean, prices_clean)

        # Load
        self.load_data(stocks_clean, prices_clean)

        print("=" * 50)
        print("✅ Financial ETL pipeline completed successfully!")

        # Summary
        print(f"\n📈 Pipeline Summary:")
        print(f"   - Stocks processed: {len(stocks_clean)}")
        print(f"   - Price records: {len(prices_clean)}")
        print(
            f"   - Date range: {prices_clean['date'].min()} to {prices_clean['date'].max()}"
        )
        print(f"   - Sectors analyzed: {stocks_clean['sector'].nunique()}")


def main():
    """Main function to run the ETL pipeline"""
    try:
        etl = FinancialETL()
        etl.run_pipeline()
    except Exception as e:
        print(f"❌ ETL Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()

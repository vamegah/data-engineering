#!/usr/bin/env python3
"""
Real-time Data Integration with Yahoo Finance API
Fetches live market data and integrates with existing pipeline
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

from shared.config.database import DatabaseConfig
from shared.utils.helpers import validate_data
import warnings

warnings.filterwarnings("ignore")


class RealTimeDataFetcher:
    def __init__(self):
        self.engine = DatabaseConfig.get_engine()

    def get_popular_stocks(self):
        """Get list of popular stocks for real-time tracking"""
        return [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "JPM",
            "JNJ",
            "V",
            "PG",
            "UNH",
            "HD",
            "DIS",
            "PYPL",
            "NFLX",
            "ADBE",
            "CRM",
            "INTC",
            "CSCO",
            "PEP",
            "T",
            "VZ",
            "ABT",
            "TMO",
            "COST",
            "LLY",
            "WMT",
            "XOM",
            "CVX",
        ]

    def fetch_stock_data(self, symbol, period="1y", interval="1d"):
        """Fetch historical data for a stock"""
        try:
            stock = yf.Ticker(symbol)

            # Get historical data
            hist_data = stock.history(period=period, interval=interval)

            if hist_data.empty:
                print(f"⚠️  No data found for {symbol}")
                return None

            # Get company info
            info = stock.info
            company_name = info.get("longName", symbol)
            sector = info.get("sector", "Unknown")
            market_cap = info.get("marketCap", 0)

            # Determine market cap category
            if market_cap > 200e9:
                market_cap_cat = "Large"
            elif market_cap > 10e9:
                market_cap_cat = "Mid"
            else:
                market_cap_cat = "Small"

            dividend_yield = info.get("dividendYield", 0) or 0

            # Prepare stock info
            stock_info = {
                "stock_id": f"YF_{symbol}",
                "symbol": symbol,
                "company_name": company_name,
                "sector": sector,
                "market_cap": market_cap_cat,
                "dividend_yield": dividend_yield,
                "data_source": "Yahoo Finance",
            }

            # Prepare price data
            hist_data = hist_data.reset_index()
            hist_data["stock_id"] = f"YF_{symbol}"
            hist_data["symbol"] = symbol
            hist_data = hist_data.rename(
                columns={
                    "Date": "date",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )

            return stock_info, hist_data

        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return None

    def fetch_real_time_quotes(self, symbols):
        """Fetch real-time quotes for multiple stocks"""
        try:
            # Use yfinance to get real-time data
            symbols_str = " ".join(symbols)
            tickers = yf.Tickers(symbols_str)

            real_time_data = []
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info
                    hist = ticker.history(period="1d", interval="1m")

                    if not hist.empty:
                        latest = hist.iloc[-1]
                        real_time_data.append(
                            {
                                "symbol": symbol,
                                "company_name": info.get("longName", symbol),
                                "current_price": latest["Close"],
                                "change": latest["Close"] - hist.iloc[0]["Close"],
                                "change_percent": (
                                    (latest["Close"] - hist.iloc[0]["Close"])
                                    / hist.iloc[0]["Close"]
                                )
                                * 100,
                                "volume": latest["Volume"],
                                "last_updated": datetime.now(),
                                "day_high": latest["High"],
                                "day_low": latest["Low"],
                            }
                        )
                except Exception as e:
                    print(f"❌ Error fetching real-time data for {symbol}: {e}")
                    continue

            return pd.DataFrame(real_time_data)

        except Exception as e:
            print(f"❌ Error in real-time quotes: {e}")
            return pd.DataFrame()

    def update_database_with_real_data(self, symbols=None):
        """Update database with real stock data"""
        if symbols is None:
            symbols = self.get_popular_stocks()

        print(f"📡 Fetching real data for {len(symbols)} stocks...")

        all_stocks_info = []
        all_prices_data = []

        for symbol in symbols:
            print(f"🔄 Fetching {symbol}...")
            result = self.fetch_stock_data(symbol)

            if result:
                stock_info, price_data = result
                all_stocks_info.append(stock_info)
                all_prices_data.append(price_data)

            # Add delay to avoid rate limiting
            time.sleep(0.5)

        if all_stocks_info and all_prices_data:
            # Combine all data
            stocks_df = pd.DataFrame(all_stocks_info)
            prices_df = pd.concat(all_prices_data, ignore_index=True)

            # Data validation
            validate_data(stocks_df, "Real Stocks Data")
            validate_data(prices_df, "Real Prices Data")

            # Save to database
            try:
                stocks_df.to_sql(
                    "stocks_real_time", self.engine, if_exists="replace", index=False
                )
                prices_df.to_sql(
                    "stock_prices_real_time",
                    self.engine,
                    if_exists="replace",
                    index=False,
                )

                print(
                    f"✅ Real data saved: {len(stocks_df)} stocks, {len(prices_df)} price records"
                )

                # Also save to CSV for backup
                stocks_df.to_csv("../data/raw/stocks_real_time.csv", index=False)
                prices_df.to_csv("../data/raw/prices_real_time.csv", index=False)

                return stocks_df, prices_df

            except Exception as e:
                print(f"❌ Database error: {e}")
                return None, None

        return None, None

    def get_market_summary(self):
        """Get current market summary"""
        try:
            # Get major indices
            indices = {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones",
                "^IXIC": "NASDAQ",
                "^RUT": "Russell 2000",
            }

            market_data = []
            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")

                    if len(hist) >= 2:
                        current = hist["Close"].iloc[-1]
                        previous = hist["Close"].iloc[-2]
                        change = current - previous
                        change_pct = (change / previous) * 100

                        market_data.append(
                            {
                                "index": name,
                                "symbol": symbol,
                                "current": current,
                                "change": change,
                                "change_pct": change_pct,
                                "status": "UP" if change > 0 else "DOWN",
                            }
                        )
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
                    continue

            return pd.DataFrame(market_data)

        except Exception as e:
            print(f"Error getting market summary: {e}")
            return pd.DataFrame()


def main():
    """Main function to fetch and update real-time data"""
    print("🚀 Starting Real-time Data Integration...")

    fetcher = RealTimeDataFetcher()

    # Update with real data
    stocks_df, prices_df = fetcher.update_database_with_real_data()

    if stocks_df is not None:
        print("\n📊 Real Data Summary:")
        print(f"Stocks: {len(stocks_df)}")
        print(f"Price records: {len(prices_df)}")
        print(f"Sectors: {stocks_df['sector'].nunique()}")
        print(f"Date range: {prices_df['date'].min()} to {prices_df['date'].max()}")

        # Get market summary
        market_summary = fetcher.get_market_summary()
        if not market_summary.empty:
            print("\n🏛️  Market Indices Summary:")
            for _, row in market_summary.iterrows():
                print(
                    f"  {row['index']}: {row['current']:.2f} ({row['change_pct']:+.2f}%)"
                )

    print("\n✅ Real-time data integration completed!")


if __name__ == "__main__":
    main()

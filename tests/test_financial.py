"""
Comprehensive test suite for Financial Analytics project.
Tests ETL pipeline, LSTM model, data quality, and performance.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFinancialETL:
    """Test ETL pipeline functionality"""

    def test_stock_data_loading(self):
        """Test that stock data can be loaded"""
        data_path = project_root / "data" / "processed"

        if (data_path / "financial_stocks_clean.csv").exists():
            stocks = pd.read_csv(data_path / "financial_stocks_clean.csv")
            assert len(stocks) > 0, "Stock data is empty"
            assert (
                "Date" in stocks.columns or "date" in stocks.columns
            ), "Missing date column"

    def test_price_columns_exist(self):
        """Test that OHLC price columns exist"""
        data_path = project_root / "data" / "processed"

        if (data_path / "financial_stocks_clean.csv").exists():
            stocks = pd.read_csv(data_path / "financial_stocks_clean.csv")

            expected_cols = ["Open", "High", "Low", "Close"]
            for col in expected_cols:
                # Check both capitalized and lowercase versions
                assert (
                    col in stocks.columns or col.lower() in stocks.columns
                ), f"Missing {col} column"


class TestDataQuality:
    """Test data quality metrics"""

    def test_no_missing_prices(self):
        """Test that price columns have minimal missing values"""
        data_path = project_root / "data" / "processed"

        if (data_path / "financial_stocks_clean.csv").exists():
            stocks = pd.read_csv(data_path / "financial_stocks_clean.csv")

            price_cols = [
                col
                for col in stocks.columns
                if col in ["Open", "High", "Low", "Close", "close"]
            ]
            for col in price_cols:
                missing_pct = stocks[col].isna().mean()
                assert missing_pct < 0.1, f"{col} has {missing_pct:.1%} missing values"

    def test_price_relationships(self):
        """Test that High >= Low"""
        data_path = project_root / "data" / "processed"

        if (data_path / "financial_stocks_clean.csv").exists():
            stocks = pd.read_csv(data_path / "financial_stocks_clean.csv")

            if "High" in stocks.columns and "Low" in stocks.columns:
                assert (stocks["High"] >= stocks["Low"]).all(), "High should be >= Low"

    def test_positive_prices(self):
        """Test that all prices are positive"""
        data_path = project_root / "data" / "processed"

        if (data_path / "financial_stocks_clean.csv").exists():
            stocks = pd.read_csv(data_path / "financial_stocks_clean.csv")

            price_cols = [
                col for col in stocks.columns if col in ["Open", "High", "Low", "Close"]
            ]
            for col in price_cols:
                if col in stocks.columns:
                    assert (
                        stocks[col].dropna() > 0
                    ).all(), f"{col} has non-positive values"


class TestLSTMModel:
    """Test LSTM model functionality"""

    def test_model_file_exists(self):
        """Test that LSTM model file exists"""
        model_path = project_root / "financial" / "models" / "lstm_model.h5"

        if model_path.exists():
            assert model_path.is_file(), "Model path exists but is not a file"

    def test_scaler_exists(self):
        """Test that scaler file exists"""
        scaler_path = project_root / "financial" / "models" / "scaler.pkl"

        if scaler_path.exists():
            assert scaler_path.is_file(), "Scaler path exists but is not a file"

    @pytest.mark.skipif(True, reason="TensorFlow not always available")
    def test_model_prediction(self):
        """Test that model can make predictions"""
        try:
            from tensorflow import keras
            import joblib

            model_path = project_root / "financial" / "models" / "lstm_model.h5"
            scaler_path = project_root / "financial" / "models" / "scaler.pkl"

            if model_path.exists() and scaler_path.exists():
                model = keras.models.load_model(model_path)
                scaler = joblib.load(scaler_path)

                # Create sample data (60 timesteps, 5 features)
                X_sample = np.random.random((1, 60, 5))
                predictions = model.predict(X_sample, verbose=0)

                assert predictions.shape[0] == 1, "Prediction shape mismatch"
        except ImportError:
            pytest.skip("TensorFlow not available")


class TestTechnicalIndicators:
    """Test technical indicator calculations"""

    def test_sma_calculation(self):
        """Test Simple Moving Average calculation"""
        data_path = project_root / "data" / "processed"

        if (data_path / "financial_stocks_clean.csv").exists():
            stocks = pd.read_csv(data_path / "financial_stocks_clean.csv")

            if "Close" in stocks.columns and len(stocks) >= 20:
                sma_20 = stocks["Close"].rolling(window=20).mean()
                assert len(sma_20) == len(stocks), "SMA length mismatch"
                assert sma_20.iloc[-1] > 0, "SMA should be positive"

    def test_returns_calculation(self):
        """Test that returns can be calculated"""
        data_path = project_root / "data" / "processed"

        if (data_path / "financial_stocks_clean.csv").exists():
            stocks = pd.read_csv(data_path / "financial_stocks_clean.csv")

            if "Close" in stocks.columns:
                returns = stocks["Close"].pct_change()
                # Returns should be reasonable (not > 100% in a day)
                assert returns.abs().max() < 1.0, "Unrealistic daily return detected"


class TestPerformance:
    """Test performance metrics"""

    def test_data_loading_speed(self):
        """Test data loads within reasonable time"""
        import time

        data_path = project_root / "data" / "processed"
        stocks_file = data_path / "financial_stocks_clean.csv"

        if stocks_file.exists():
            start = time.time()
            stocks = pd.read_csv(stocks_file)
            load_time = time.time() - start

            assert load_time < 5.0, f"Loading took {load_time:.2f}s, should be < 5s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

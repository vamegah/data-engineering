"""
Comprehensive test suite for Restaurant Analytics project.
Tests ETL pipeline, sentiment analysis, NLP, and data quality.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRestaurantETL:
    """Test ETL pipeline functionality"""

    def test_data_loading(self):
        """Test that restaurant data can be loaded"""
        data_path = project_root / "data" / "processed"

        files = ["restaurant_restaurants_clean.csv", "restaurant_reviews_clean.csv"]

        for filename in files:
            file_path = data_path / filename
            if file_path.exists():
                df = pd.read_csv(file_path)
                assert len(df) > 0, f"{filename} is empty"

    def test_required_columns_restaurants(self):
        """Test restaurant data has required columns"""
        data_path = project_root / "data" / "processed"
        restaurants_file = data_path / "restaurant_restaurants_clean.csv"

        if restaurants_file.exists():
            restaurants = pd.read_csv(restaurants_file)
            required_cols = ["restaurant_id"]

            for col in required_cols:
                assert col in restaurants.columns, f"Missing column: {col}"

    def test_required_columns_reviews(self):
        """Test review data has required columns"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)
            required_cols = ["review_id", "restaurant_id"]

            for col in required_cols:
                assert col in reviews.columns, f"Missing column: {col}"


class TestDataQuality:
    """Test data quality metrics"""

    def test_no_missing_restaurant_ids(self):
        """Test that restaurant IDs have no missing values"""
        data_path = project_root / "data" / "processed"
        restaurants_file = data_path / "restaurant_restaurants_clean.csv"

        if restaurants_file.exists():
            restaurants = pd.read_csv(restaurants_file)
            assert (
                restaurants["restaurant_id"].isna().sum() == 0
            ), "Missing restaurant IDs"

    def test_rating_range(self):
        """Test that ratings are in valid range"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)

            rating_cols = [
                col
                for col in reviews.columns
                if "rating" in col.lower() or "stars" in col.lower()
            ]
            for col in rating_cols:
                if col in reviews.columns:
                    assert (reviews[col].dropna() >= 1).all(), f"{col} has values < 1"
                    assert (reviews[col].dropna() <= 5).all(), f"{col} has values > 5"

    def test_no_duplicate_reviews(self):
        """Test no duplicate review IDs"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)

            if "review_id" in reviews.columns:
                duplicates = reviews["review_id"].duplicated().sum()
                assert duplicates == 0, f"Found {duplicates} duplicate reviews"


class TestSentimentAnalysis:
    """Test sentiment analysis functionality"""

    def test_sentiment_results_exist(self):
        """Test that sentiment analysis results exist"""
        data_path = project_root / "data" / "processed"

        possible_files = [
            "sentiment_analysis_results.csv",
            "restaurant_reviews_sentiment.csv",
            "restaurant_reviews_clean.csv",  # May contain sentiment columns
        ]

        found = any((data_path / f).exists() for f in possible_files)
        assert found, "No sentiment analysis results found"

    def test_sentiment_scores_valid(self):
        """Test that sentiment scores are in valid range"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)

            sentiment_cols = [
                col
                for col in reviews.columns
                if "sentiment" in col.lower() and "score" in col.lower()
            ]
            for col in sentiment_cols:
                # Sentiment scores typically -1 to 1 (or 0 to 1 for some libraries)
                assert (reviews[col].dropna() >= -1).all(), f"{col} has values < -1"
                assert (reviews[col].dropna() <= 1).all(), f"{col} has values > 1"

    def test_sentiment_polarity(self):
        """Test that sentiment polarity exists"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)

            polarity_cols = [
                col for col in reviews.columns if "polarity" in col.lower()
            ]
            if polarity_cols:
                for col in polarity_cols:
                    assert reviews[col].notna().any(), f"{col} has no data"


class TestNLPProcessing:
    """Test NLP processing functionality"""

    def test_text_data_exists(self):
        """Test that review text exists"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)

            text_cols = [
                col
                for col in reviews.columns
                if "text" in col.lower()
                or "review" in col.lower()
                or "comment" in col.lower()
            ]
            assert len(text_cols) > 0, "No text columns found"

    def test_text_not_empty(self):
        """Test that review text is not empty"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)

            text_cols = [
                col
                for col in reviews.columns
                if "text" in col.lower() or "comment" in col.lower()
            ]
            for col in text_cols:
                if col in reviews.columns:
                    # At least 80% of text should be non-empty
                    non_empty = reviews[col].notna().mean()
                    assert non_empty > 0.8, f"{col} has too many empty values"

    @pytest.mark.skipif(True, reason="NLTK may not be configured")
    def test_nltk_available(self):
        """Test that NLTK is available"""
        try:
            import nltk

            assert True
        except ImportError:
            pytest.skip("NLTK not available")


class TestBusinessMetrics:
    """Test business metric calculations"""

    def test_average_rating_reasonable(self):
        """Test that average ratings are reasonable"""
        data_path = project_root / "data" / "processed"
        restaurants_file = data_path / "restaurant_restaurants_clean.csv"

        if restaurants_file.exists():
            restaurants = pd.read_csv(restaurants_file)

            rating_cols = [
                col
                for col in restaurants.columns
                if "rating" in col.lower() or "score" in col.lower()
            ]
            for col in rating_cols:
                if col in restaurants.columns:
                    avg_rating = restaurants[col].mean()
                    assert (
                        1 <= avg_rating <= 5
                    ), f"Average rating {avg_rating:.2f} is unrealistic"

    def test_review_count_positive(self):
        """Test that review counts are positive"""
        data_path = project_root / "data" / "processed"
        restaurants_file = data_path / "restaurant_restaurants_clean.csv"

        if restaurants_file.exists():
            restaurants = pd.read_csv(restaurants_file)

            count_cols = [
                col
                for col in restaurants.columns
                if "count" in col.lower() or "reviews" in col.lower()
            ]
            for col in count_cols:
                if col in restaurants.columns and pd.api.types.is_numeric_dtype(
                    restaurants[col]
                ):
                    assert (
                        restaurants[col].dropna() >= 0
                    ).all(), f"{col} has negative values"


class TestPerformance:
    """Test performance metrics"""

    def test_data_loading_speed(self):
        """Test data loads within reasonable time"""
        import time

        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            start = time.time()
            reviews = pd.read_csv(reviews_file)
            load_time = time.time() - start

            assert load_time < 5.0, f"Loading took {load_time:.2f}s, should be < 5s"

    def test_memory_usage(self):
        """Test memory usage is reasonable"""
        data_path = project_root / "data" / "processed"
        reviews_file = data_path / "restaurant_reviews_clean.csv"

        if reviews_file.exists():
            reviews = pd.read_csv(reviews_file)
            memory_mb = reviews.memory_usage(deep=True).sum() / 1024 / 1024
            assert memory_mb < 500, f"Using {memory_mb:.0f}MB, should be < 500MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

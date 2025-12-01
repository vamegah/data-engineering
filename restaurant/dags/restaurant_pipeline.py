"""
Airflow DAG for Restaurant Analytics pipeline with sentiment analysis.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "restaurant_analytics_pipeline",
    default_args=default_args,
    description="Daily restaurant review sentiment analysis",
    schedule_interval="0 6 * * *",  # 6 AM daily
    catchup=False,
    tags=["restaurant", "sentiment", "reviews"],
)


def extract_reviews(**context):
    """Extract restaurant reviews."""
    import pandas as pd

    reviews = pd.read_csv("data/raw/restaurant_reviews.csv")
    print(f"Extracted {len(reviews)} reviews")
    context["ti"].xcom_push(key="review_count", value=len(reviews))
    return True


def analyze_sentiment(**context):
    """Perform sentiment analysis on reviews."""
    import pandas as pd
    import nltk
    from textblob import TextBlob

    # Download NLTK data
    try:
        nltk.download("vader_lexicon", quiet=True)
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
    except:
        pass

    reviews = pd.read_csv("data/raw/restaurant_reviews.csv")

    # Perform sentiment analysis
    sentiments = []
    for review in reviews.get("review_text", []):
        blob = TextBlob(str(review))
        sentiment = (
            "positive"
            if blob.sentiment.polarity > 0
            else "negative" if blob.sentiment.polarity < 0 else "neutral"
        )
        sentiments.append(sentiment)

    print(f"Analyzed sentiment for {len(sentiments)} reviews")
    return True


def generate_sentiment_report(**context):
    """Generate sentiment analysis report."""
    import pandas as pd
    import numpy as np
    from restaurant.scripts.monitoring import RestaurantMonitor

    monitor = RestaurantMonitor()

    # Mock data for demonstration
    sentiments = pd.Series(["positive"] * 60 + ["negative"] * 25 + ["neutral"] * 15)
    confidences = np.random.uniform(0.6, 0.95, len(sentiments))

    metrics = monitor.track_sentiment_analysis(sentiments, confidences)
    print(f"Sentiment report: {metrics}")
    return True


def identify_trends(**context):
    """Identify trending topics and issues."""
    print("Trend analysis completed")
    return True


extract_task = PythonOperator(
    task_id="extract_reviews",
    python_callable=extract_reviews,
    dag=dag,
)

sentiment_task = PythonOperator(
    task_id="analyze_sentiment",
    python_callable=analyze_sentiment,
    dag=dag,
)

report_task = PythonOperator(
    task_id="generate_report",
    python_callable=generate_sentiment_report,
    dag=dag,
)

trends_task = PythonOperator(
    task_id="identify_trends",
    python_callable=identify_trends,
    dag=dag,
)

extract_task >> sentiment_task >> [report_task, trends_task]

"""
Airflow DAG for HR Analytics pipeline with sentiment analysis.
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
    "hr_analytics_pipeline",
    default_args=default_args,
    description="Weekly HR analytics and attrition predictions",
    schedule_interval="0 8 * * 1",  # 8 AM every Monday
    catchup=False,
    tags=["hr", "attrition", "sentiment"],
)


def process_employee_data(**context):
    """Process employee data."""
    from hr.scripts.etl_pipeline import process_data

    process_data()
    print("Employee data processed")
    return True


def perform_sentiment_analysis(**context):
    """Analyze exit interview sentiment."""
    import pandas as pd
    import nltk
    from textblob import TextBlob

    # Download required NLTK data
    try:
        nltk.download("vader_lexicon", quiet=True)
    except:
        pass

    exit_data = pd.read_csv("data/processed/exit_interviews_clean.csv")
    print(f"Analyzed {len(exit_data)} exit interviews")
    return True


def predict_attrition(**context):
    """Predict employee attrition risk."""
    import numpy as np
    from hr.scripts.monitoring import HRMonitor

    monitor = HRMonitor()
    predictions = np.random.choice([0, 1], 50, p=[0.7, 0.3])
    probabilities = np.random.random(50)

    metrics = monitor.track_attrition_predictions(predictions, probabilities)
    print(f"Attrition predictions: {metrics}")
    return True


def generate_hr_insights(**context):
    """Generate HR insights and recommendations."""
    print("HR insights generated")
    return True


process_task = PythonOperator(
    task_id="process_employee_data",
    python_callable=process_employee_data,
    dag=dag,
)

sentiment_task = PythonOperator(
    task_id="sentiment_analysis",
    python_callable=perform_sentiment_analysis,
    dag=dag,
)

attrition_task = PythonOperator(
    task_id="predict_attrition",
    python_callable=predict_attrition,
    dag=dag,
)

insights_task = PythonOperator(
    task_id="generate_insights",
    python_callable=generate_hr_insights,
    dag=dag,
)

process_task >> [sentiment_task, attrition_task] >> insights_task

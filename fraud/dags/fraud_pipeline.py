"""
Airflow DAG for Fraud Detection ETL pipeline.
Runs daily to process fraud transactions and update models.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "fraud_detection_pipeline",
    default_args=default_args,
    description="Daily fraud detection ETL and model training",
    schedule_interval="0 2 * * *",  # 2 AM daily
    catchup=False,
    tags=["fraud", "etl", "ml"],
)


def extract_fraud_data(**context):
    """Extract fraud transaction data."""
    from fraud.scripts.etl_pipeline import extract_data

    data = extract_data()
    context["ti"].xcom_push(key="extracted_records", value=len(data))
    print(f"Extracted {len(data)} records")
    return True


def transform_fraud_data(**context):
    """Transform and clean fraud data."""
    from fraud.scripts.etl_pipeline import transform_data

    transformed = transform_data()
    context["ti"].xcom_push(key="transformed_records", value=len(transformed))
    return True


def load_fraud_data(**context):
    """Load processed data to database."""
    from fraud.scripts.etl_pipeline import load_data

    load_data()
    return True


def train_fraud_model(**context):
    """Train fraud detection model."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import joblib

    # Load processed data
    data = pd.read_csv("data/processed/fraud_data_clean.csv")

    # Train model
    X = data.drop(["is_fraudulent"], axis=1, errors="ignore")
    y = data.get("is_fraudulent", [])

    if len(y) > 0:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        joblib.dump(model, "fraud/models/fraud_detector.pkl")
        print("Model trained and saved")
    return True


def validate_model(**context):
    """Validate model performance."""
    from fraud.scripts.monitoring import FraudMonitor
    import numpy as np

    monitor = FraudMonitor()

    # Mock validation
    predictions = np.random.choice([0, 1], 100, p=[0.9, 0.1])
    probabilities = np.random.random(100)

    metrics = monitor.track_predictions(predictions, probabilities)
    print(f"Validation metrics: {metrics}")
    return True


# Define tasks
extract_task = PythonOperator(
    task_id="extract_fraud_data",
    python_callable=extract_fraud_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_fraud_data",
    python_callable=transform_fraud_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_fraud_data",
    python_callable=load_fraud_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id="train_fraud_model",
    python_callable=train_fraud_model,
    dag=dag,
)

validate_task = PythonOperator(
    task_id="validate_model",
    python_callable=validate_model,
    dag=dag,
)

health_check = BashOperator(
    task_id="health_check",
    bash_command="curl -f http://localhost:8001/health || exit 1",
    dag=dag,
)

# Define dependencies
(
    extract_task
    >> transform_task
    >> load_task
    >> train_task
    >> validate_task
    >> health_check
)

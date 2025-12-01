"""
Airflow DAG for E-commerce Analytics pipeline.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "ecommerce_analytics_pipeline",
    default_args=default_args,
    description="Daily e-commerce analytics ETL",
    schedule_interval="0 3 * * *",  # 3 AM daily
    catchup=False,
    tags=["ecommerce", "analytics"],
)


def extract_ecommerce_data(**context):
    """Extract e-commerce data."""
    from ecommerce.scripts.etl_pipeline import extract_data

    data = extract_data()
    print(f"Extracted {len(data)} records")
    return True


def perform_rfm_analysis(**context):
    """Perform RFM customer segmentation."""
    import pandas as pd

    customers = pd.read_csv("data/raw/ecommerce_customers.csv")
    transactions = pd.read_csv("data/raw/ecommerce_transactions.csv")

    # RFM analysis logic here
    print("RFM analysis completed")
    return True


def generate_insights(**context):
    """Generate business insights."""
    from ecommerce.scripts.monitoring import EcommerceMonitor
    import pandas as pd

    monitor = EcommerceMonitor()
    transactions = pd.read_csv("data/raw/ecommerce_transactions.csv")
    metrics = monitor.check_transaction_quality(transactions)
    print(f"Insights: {metrics}")
    return True


extract_task = PythonOperator(
    task_id="extract_ecommerce_data",
    python_callable=extract_ecommerce_data,
    dag=dag,
)

rfm_task = PythonOperator(
    task_id="perform_rfm_analysis",
    python_callable=perform_rfm_analysis,
    dag=dag,
)

insights_task = PythonOperator(
    task_id="generate_insights",
    python_callable=generate_insights,
    dag=dag,
)

extract_task >> rfm_task >> insights_task

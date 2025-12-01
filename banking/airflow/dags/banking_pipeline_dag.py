"""
Apache Airflow DAG for Banking Churn Pipeline
Orchestrates daily ETL, weekly model training, and monitoring
"""

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os

# Add project to path
sys.path.insert(0, "/app")  # Adjust based on your deployment

from banking.scripts.etl_pipeline import run_etl_pipeline
from banking.scripts.monitoring import monitor_etl_pipeline, SystemMetricsMonitor
import pandas as pd

# Default arguments
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["alerts@yourcompany.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": days_ago(1),
}

# Create DAG
dag = DAG(
    "banking_churn_pipeline",
    default_args=default_args,
    description="Daily ETL and weekly model training for banking churn prediction",
    schedule_interval="0 2 * * *",  # Run daily at 2 AM
    catchup=False,
    tags=["banking", "churn", "ml"],
)


def check_data_files(**context):
    """Check that required data files exist"""
    required_files = [
        "/app/banking/data/raw/banking_customers.csv",
        "/app/banking/data/raw/banking_transactions.csv",
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        raise FileNotFoundError(f"Missing required files: {missing_files}")

    print("✅ All required data files present")
    return True


def run_etl(**context):
    """Execute ETL pipeline"""
    print("🚀 Starting ETL pipeline...")
    success = run_etl_pipeline(source_type="csv", destination_type="both")

    if not success:
        raise Exception("ETL pipeline failed")

    print("✅ ETL pipeline completed successfully")
    return success


def run_quality_checks(**context):
    """Run data quality monitoring"""
    print("🔍 Running data quality checks...")

    # Load processed data
    customers = pd.read_csv("/app/banking/data/processed/banking_customers_clean.csv")
    transactions = pd.read_csv(
        "/app/banking/data/processed/banking_transactions_clean.csv"
    )

    # Run monitoring
    metrics = monitor_etl_pipeline(customers, transactions)

    # Check for critical issues
    total_alerts = len(metrics["customers"]["alerts"]) + len(
        metrics["transactions"]["alerts"]
    )

    if total_alerts > 5:
        print(f"⚠️ Warning: {total_alerts} data quality alerts detected")
    else:
        print(f"✅ Quality checks passed ({total_alerts} minor alerts)")

    # Push metrics to XCom for downstream tasks
    context["task_instance"].xcom_push(key="quality_metrics", value=metrics)

    return metrics


def check_system_health(**context):
    """Check system health and resources"""
    print("💻 Checking system health...")

    monitor = SystemMetricsMonitor()
    health = monitor.health_check()
    metrics = monitor.get_system_metrics()

    # Alert on resource issues
    if metrics["cpu_percent"] > 80:
        print(f"⚠️ High CPU usage: {metrics['cpu_percent']}%")

    if metrics["memory"]["percent_used"] > 85:
        print(f"⚠️ High memory usage: {metrics['memory']['percent_used']}%")

    if health["status"] != "healthy":
        print(f"⚠️ System health: {health['status']}")
    else:
        print("✅ System health: healthy")

    return health


def train_model(**context):
    """Train/retrain ML model (weekly)"""
    print("🤖 Training ML model...")

    # This would trigger notebook execution or call training script
    # For now, just log
    print("Model training scheduled (implement with papermill or custom script)")

    # Example: Run notebook with papermill
    # import papermill as pm
    # pm.execute_notebook(
    #     '/app/banking/notebooks/03_churn_prediction.ipynb',
    #     '/app/banking/logs/model_training_output.ipynb',
    #     parameters={'retrain': True}
    # )

    return True


def send_summary_email(**context):
    """Send daily summary email"""
    print("📧 Sending summary email...")

    # Get metrics from XCom
    quality_metrics = context["task_instance"].xcom_pull(
        key="quality_metrics", task_ids="quality_checks"
    )

    # Build summary
    summary = f"""
    Banking Churn Pipeline - Daily Summary
    Date: {datetime.now().strftime('%Y-%m-%d')}
    
    ETL Pipeline: ✅ Success
    Customers Processed: {quality_metrics['customers']['total_rows']:,}
    Transactions Processed: {quality_metrics['transactions']['total_rows']:,}
    Quality Alerts: {len(quality_metrics['customers']['alerts']) + len(quality_metrics['transactions']['alerts'])}
    
    Status: All systems operational
    """

    print(summary)
    # Implement actual email sending here

    return summary


# Define tasks

check_files_task = PythonOperator(
    task_id="check_data_files",
    python_callable=check_data_files,
    provide_context=True,
    dag=dag,
)

system_health_task = PythonOperator(
    task_id="system_health_check",
    python_callable=check_system_health,
    provide_context=True,
    dag=dag,
)

etl_task = PythonOperator(
    task_id="run_etl_pipeline",
    python_callable=run_etl,
    provide_context=True,
    dag=dag,
)

quality_task = PythonOperator(
    task_id="quality_checks",
    python_callable=run_quality_checks,
    provide_context=True,
    dag=dag,
)

# Backup task
backup_task = BashOperator(
    task_id="backup_data",
    bash_command="cp -r /app/banking/data/processed /app/banking/data/backups/$(date +%Y%m%d)/",
    dag=dag,
)

summary_task = PythonOperator(
    task_id="send_summary",
    python_callable=send_summary_email,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
(
    check_files_task
    >> system_health_task
    >> etl_task
    >> quality_task
    >> [backup_task, summary_task]
)


# Weekly model retraining DAG
dag_weekly = DAG(
    "banking_churn_model_training",
    default_args=default_args,
    description="Weekly model retraining",
    schedule_interval="0 3 * * 0",  # Run Sundays at 3 AM
    catchup=False,
    tags=["banking", "churn", "ml", "training"],
)

train_task = PythonOperator(
    task_id="train_model",
    python_callable=train_model,
    provide_context=True,
    dag=dag_weekly,
)

# Validate model performance after training
validate_task = BashOperator(
    task_id="validate_model",
    bash_command="python /app/banking/scripts/validate_model.py",
    dag=dag_weekly,
)

train_task >> validate_task

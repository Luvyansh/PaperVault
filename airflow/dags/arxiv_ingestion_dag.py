import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from celery import Celery

logger = logging.getLogger(__name__)

# Standalone Celery client that points to your Redis broker via Docker networking.
# This prevents Airflow from needing to import ANY of your custom backend code!
external_celery = Celery('airflow_dispatcher', broker='redis://redis:6379/0')

def trigger_pipeline(**kwargs):
    """Sends a generic trigger message to the Celery worker."""
    logger.info("Sending trigger message to backend Celery workers...")
    
    # We trigger the master task you just added to tasks.py
    external_celery.send_task(
        name="app.etl.tasks.fetch_daily_papers",
        queue="ingestion"
    )
    return "Master task triggered."

default_args = {
    'owner': 'anurag',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_arxiv_ingestion',
    default_args=default_args,
    description='Triggers the backend pipeline to fetch and process AI papers',
    schedule_interval='0 2 * * *',
    start_date=datetime(2026, 4, 20),
    catchup=False,
    tags=['etl', 'arxiv', 'rag'],
) as dag:

    trigger_task = PythonOperator(
        task_id='trigger_master_pipeline',
        python_callable=trigger_pipeline,
    )
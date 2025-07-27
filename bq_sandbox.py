"""Server-side training DAG definition"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")

from callables import get_bq_sandbox_usage

ORCHESTRATION_SA = "airflow-prod-sa"

default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime(2022, 2, 21),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@newco.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
if DEPLOYMENT_TYPE is None:
    schedule_interval = '0 1 * * *'
elif DEPLOYMENT_TYPE == 'DEV':
    schedule_interval = None
else:
    raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

with DAG('BQ_Sandbox_Costs', default_args=default_args, schedule_interval=schedule_interval, catchup=False) as dag:
    # GATHER RESOURCE USAGE INFORMATION
    get_usage_info = PythonOperator(task_id='get-bq-sandbox-usage-info',
                                    provide_context=True,
                                    python_callable=get_bq_sandbox_usage)

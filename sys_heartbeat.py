"""Build metamodel DAG definition"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")
from callables import heartbeat_via_email

default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@newco.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
if DEPLOYMENT_TYPE is None:
        schedule_interval = "0 4 * * *"
elif DEPLOYMENT_TYPE == 'DEV':
    schedule_interval = None
else:
    raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

with DAG('SYS_Heartbeat', default_args=default_args, schedule_interval=schedule_interval, catchup=False) as dag:

    heartbeat_email_notification = PythonOperator(task_id='heartbeat-email-notification',
                                                  provide_context=True,
                                                  python_callable=heartbeat_via_email)

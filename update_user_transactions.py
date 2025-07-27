"""Server-side training DAG definition"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")

from callables import update_user_transactions, update_user_credits_and_wallet

ORCHESTRATION_SA = "airflow-prod-sa"

default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime(2022, 3, 5),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@newco.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
if DEPLOYMENT_TYPE is None:
    schedule_interval = '*/10 * * * *'
elif DEPLOYMENT_TYPE == 'DEV':
    schedule_interval = None
else:
    raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

with DAG('Update_User_Transactions', default_args=default_args, schedule_interval=schedule_interval, catchup=False) as dag:
    # GATHER RESOURCE USAGE INFORMATION
    update_transactions = PythonOperator(task_id='update-user-transactions',
                                         provide_context=True,
                                         python_callable=update_user_transactions)

    update_credits_and_wallet = PythonOperator(task_id='update-credits-and-wallet',
                                               provide_context=True,
                                               python_callable=update_user_credits_and_wallet)

    update_transactions >> update_credits_and_wallet

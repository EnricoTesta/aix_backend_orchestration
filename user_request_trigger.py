"""Server-side training DAG definition"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

import sys
sys.path.insert(0, "/root/airflow/dags/backend/")
from globals import CHALLENGES
from callables import trigger_user_requests

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

for key, challenge in CHALLENGES.items():

    DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
    if DEPLOYMENT_TYPE is None:
        schedule_interval = challenge['user_request_trigger_schedule']
    elif DEPLOYMENT_TYPE == 'DEV':
        schedule_interval = None
    else:
        raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

    dag_id = f'{key}_trigger_user_requests'
    with DAG(dag_id, default_args=default_args, schedule_interval=schedule_interval, catchup=False) as dag:

        # GATHER RESOURCE USAGE INFORMATION
        trigger_requests = PythonOperator(task_id='trigger-user-requests',
                                          provide_context=True,
                                          depends_on_past=False,
                                          python_callable=trigger_user_requests,
                                          op_kwargs={'project': challenge['project_name'],
                                                     'bucket': challenge['bucket'],
                                                     'active': challenge['active']})

        globals()[dag_id] = dag

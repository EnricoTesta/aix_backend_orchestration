"""Build metamodel DAG definition"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")
from callables import get_inactive_users, reminder_via_email
from globals import CHALLENGES

default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime(2022, 4, 7),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@newco.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

for key, challenge in CHALLENGES.items():

    DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
    if DEPLOYMENT_TYPE is None:
        if challenge['email']['schedule'] == '':
            schedule_interval = None
        else:
            schedule_interval = challenge['email']['schedule']
    elif DEPLOYMENT_TYPE == 'DEV':
        schedule_interval = None
    else:
        raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

    dag_id = f'{key}_user_join_round_reminder'
    with DAG(dag_id, default_args=default_args, schedule_interval=schedule_interval, catchup=False) as dag:

        inactive_users = PythonOperator(task_id='inactive-users',
                                        provide_context=True,
                                        python_callable=get_inactive_users,
                                        op_kwargs={'challenge': challenge['name']})

        send_email_notification = PythonOperator(task_id='send-email-notification',
                                                 provide_context=True,
                                                 python_callable=reminder_via_email,
                                                 op_kwargs={'challenge': challenge['display_name'],
                                                            'until': challenge['email']['until']})

        inactive_users >> send_email_notification

        globals()[dag_id] = dag

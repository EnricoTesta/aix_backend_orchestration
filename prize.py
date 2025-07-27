"""Build metamodel DAG definition"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from yaml import safe_load
import os
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")
from callables import build_metamodel, assign_prizes, assign_prize_pool, update_transaction_w_prize, update_leaderboard
from globals import CHALLENGES


default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime(2022, 10, 15),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@newco.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

for key, challenge in CHALLENGES.items():

    DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
    if DEPLOYMENT_TYPE is None:
        if challenge['prize']['assignment_schedule'] == '':
            schedule_interval = None
        else:
            schedule_interval = challenge['prize']['assignment_schedule']
    elif DEPLOYMENT_TYPE == 'DEV':
        schedule_interval = None
    else:
        raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

    dag_id = f'{key}_prize_assignment'
    with DAG(dag_id, default_args=default_args,
             schedule_interval=schedule_interval, catchup=False) as dag:

        # Signals targets 20d arrive 6 weeks later. Since airflow runs @ the end of the interval,
        # reference date is a friday, and DAG is scheduled on monday must offset by -37 days (-7*5 - 2).
        # Update. Now targets are weekly (independent from signals). Therefore offset should be -2.
        build_metamodel_task = PythonOperator(task_id='build-metamodel',
                                              provide_context=True,
                                              python_callable=build_metamodel,
                                              op_kwargs={** challenge['prize']['build_metamodel'],
                                                         'challenge_dict': challenge})

        assign_prize_pool_task = PythonOperator(task_id='assign-prize-pool',
                                                provide_context=True,
                                                python_callable=assign_prize_pool,
                                                op_kwargs={'ref_date': challenge['prize']['ref_date'],
                                                           'problem_id': challenge['name'],
                                                           'amount': challenge['prize']['amount']}
                                                )

        assign_prizes_task = PythonOperator(task_id='assign-prizes',
                                            provide_context=True,
                                            python_callable=assign_prizes,
                                            op_kwargs={'ref_date': challenge['prize']['ref_date'],
                                                       'problem_id': challenge['name'],
                                                       'source_uri': challenge['prize']['assign_prizes_source_uri']}
                                            )

        update_transactions_w_prize_task = PythonOperator(task_id='update-transactions-w-prize',
                                                          provide_context=True,
                                                          python_callable=update_transaction_w_prize,
                                                          op_kwargs={'ref_date': challenge['prize']['ref_date'],
                                                                     'problem_id': challenge['name']}
                                                          )

        update_leaderboard_task = PythonOperator(task_id='update-leaderboard',
                                                 provide_context=True,
                                                 python_callable=update_leaderboard)

        build_metamodel_task >> [assign_prizes_task,
                                 assign_prize_pool_task] >> update_transactions_w_prize_task >> update_leaderboard_task

        globals()[dag_id] = dag

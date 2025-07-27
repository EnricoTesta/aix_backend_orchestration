"""Build metamodel DAG definition"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")
from operators import InferenceSensorOperator
from callables import build_metamodel, trigger_inference_jobs, \
    score_metamodel, delete_data_from_gcs, create_inference_dataset_for_backfill, \
    reset_user_sub_status
from globals import CHALLENGES


default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime(2022, 2, 26),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@newco.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

for key, challenge in CHALLENGES.items():

    DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
    if DEPLOYMENT_TYPE is None:
        if challenge['inference']['schedule'] == '':
            schedule_interval = None
        else:
            schedule_interval = challenge['inference']['schedule']
    elif DEPLOYMENT_TYPE == 'DEV':
        schedule_interval = None
    else:
        raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

    dag_id = f'{key}_inference_orchestration'
    with DAG(dag_id, default_args=default_args, schedule_interval=schedule_interval, catchup=False) as dag:

        clear_inference = PythonOperator(task_id='clear-inference',
                                         provide_context=True,
                                         python_callable=delete_data_from_gcs,
                                         op_kwargs={'data_gcs_path': challenge['inference']['inference_data_gcs_path']})

        clear_inference_logs = PythonOperator(task_id='clear-inference-logs',
                                              provide_context=True,
                                              python_callable=delete_data_from_gcs,
                                              op_kwargs={'data_gcs_path': challenge['inference']['logs_data_gcs_path']})

        clear_metamodel = PythonOperator(task_id='clear-metamodel',
                                         provide_context=True,
                                         python_callable=delete_data_from_gcs,
                                         op_kwargs={'data_gcs_path': challenge['inference']['metamodel_data_gcs_path']})

        # backfill_inference_dataset = PythonOperator(task_id='backfill-inference-dataset',
        #                                            provide_context=True,
        #                                            wait_for_downstream=True,  # wait for past DAGs complete execution
        #                                            python_callable=create_inference_dataset_for_backfill,
        #                                            op_kwargs={'obs_date': '{{ macros.ds_add(ds, 5) }}'})

        trigger_inference_jobs_tasks = PythonOperator(task_id='trigger-inference-jobs',
                                                      provide_context=True,
                                                      python_callable=trigger_inference_jobs,
                                                      op_kwargs={'obs_date': challenge['inference']['obs_date'],
                                                                 'artifact_bucket': challenge['inference']['bucket'],
                                                                 'artifact_prefix': challenge['inference']['artifact_prefix'],
                                                                 'active_prefix': challenge['inference']['active_prefix'],
                                                                 'active_user_destination_uri': challenge['inference']['active_user_destination_uri'],
                                                                 'environment': DEPLOYMENT_TYPE,
                                                                 'challenge_dict': challenge})

        wait_inference_jobs = InferenceSensorOperator(task_id='wait-inference-jobs',
                                                      poke_interval=120,
                                                      timeout=3600,
                                                      mode='reschedule',
                                                      poke_kwargs={'bucket': challenge['inference']['bucket'],
                                                                   'prefix': challenge['inference']['wait_inference_jobs_prefix']})

        build_metamodel_task = PythonOperator(task_id='build-metamodel',
                                              provide_context=True,
                                              python_callable=build_metamodel,
                                              op_kwargs={** challenge['inference']['build_metamodel'],
                                                         'challenge_dict': challenge})

        score_metamodel_task = PythonOperator(task_id='score-metamodel',
                                              provide_context=True,
                                              python_callable=score_metamodel,
                                              op_kwargs=challenge['inference']['score_metamodel'])

        reset_user_submission_status = PythonOperator(task_id='reset-user-submission-status',
                                                      python_callable=reset_user_sub_status,
                                                      op_kwargs={'active_users_uri': challenge['inference']['reset_submission_active_users_uri'],
                                                                 'challenge': challenge['name']})

        [clear_inference, clear_inference_logs, clear_metamodel] >> trigger_inference_jobs_tasks
        # backfill_inference_dataset >> [trigger_inference_jobs_tasks, wait_inference_jobs, build_metamodel_task, score_metamodel_task]
        trigger_inference_jobs_tasks >> build_metamodel_task
        build_metamodel_task >> wait_inference_jobs
        wait_inference_jobs >> score_metamodel_task >> reset_user_submission_status

        globals()[dag_id] = dag

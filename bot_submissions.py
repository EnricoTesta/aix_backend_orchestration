"""Build metamodel DAG definition"""
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")

from callables import submit_bot_code, bot_trigger, activate_bot_submissions
from globals import CHALLENGES

default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime(2022, 5, 27),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@newco.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}


for key, challenge in CHALLENGES.items():

    DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
    if DEPLOYMENT_TYPE is None:
        if challenge['bot_submission_trigger_schedule'] == '':
            schedule_interval = None
        else:
            schedule_interval = challenge['bot_submission_trigger_schedule']
    elif DEPLOYMENT_TYPE == 'DEV':
        schedule_interval = None
    else:
        raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

    dag_id = f'{key}_bot_submission'

    with DAG(dag_id, default_args=default_args, schedule_interval=schedule_interval, catchup=False) as dag:
        # DUMMY
        upload_dummy_bot = PythonOperator(task_id='upload-dummy-bot',
                                          provide_context=True,
                                          python_callable=submit_bot_code,
                                          op_kwargs={'bot_name': 'bot_dummy',
                                                     'challenge': challenge['name']})

        trigger_dummy_bot = PythonOperator(task_id='trigger-dummy-bot',
                                           provide_context=True,
                                           python_callable=bot_trigger,
                                           op_kwargs={'bot_name': 'bot_dummy',
                                                      'challenge': challenge['name']})

        # LGBM
        upload_lgbm_bot = PythonOperator(task_id='upload-lgbm-bot',
                                         provide_context=True,
                                         python_callable=submit_bot_code,
                                         op_kwargs={'bot_name': 'bot_lgbm',
                                                    'challenge': challenge['name']})

        trigger_lgbm_bot = PythonOperator(task_id='trigger-lgbm-bot',
                                          provide_context=True,
                                          python_callable=bot_trigger,
                                          op_kwargs={'bot_name': 'bot_lgbm',
                                                     'challenge': challenge['name']})

        # SKLEARN
        upload_sklearn_bot = PythonOperator(task_id='upload-sklearn-bot',
                                            provide_context=True,
                                            python_callable=submit_bot_code,
                                            op_kwargs={'bot_name': 'bot_sklearn',
                                                       'challenge': challenge['name']})

        trigger_sklearn_bot = PythonOperator(task_id='trigger-sklearn-bot',
                                             provide_context=True,
                                             python_callable=bot_trigger,
                                             op_kwargs={'bot_name': 'bot_sklearn',
                                                        'challenge': challenge['name']})

        # STEAL
        upload_steal_bot = PythonOperator(task_id='upload-steal-bot',
                                          provide_context=True,
                                          python_callable=submit_bot_code,
                                          op_kwargs={'bot_name': 'bot_steal',
                                                     'challenge': challenge['name']})

        trigger_steal_bot = PythonOperator(task_id='trigger-steal-bot',
                                           provide_context=True,
                                           python_callable=bot_trigger,
                                           op_kwargs={'bot_name': 'bot_steal',
                                                      'challenge': challenge['name']})

        # PYTORCH
        upload_pytorch_bot = PythonOperator(task_id='upload-pytorch-bot',
                                            provide_context=True,
                                            python_callable=submit_bot_code,
                                            op_kwargs={'bot_name': 'bot_pytorch',
                                                       'challenge': challenge['name']})

        trigger_pytorch_bot = PythonOperator(task_id='trigger-pytorch-bot',
                                             provide_context=True,
                                             python_callable=bot_trigger,
                                             op_kwargs={'bot_name': 'bot_pytorch',
                                                        'challenge': challenge['name']})

        # AIX BOT 01
        upload_bot_01 = PythonOperator(task_id='upload-aix-bot-01',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_01',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_01 = PythonOperator(task_id='trigger-aix-bot-01',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_01',
                                                       'challenge': challenge['name']})

        # AIX BOT 02
        upload_bot_02 = PythonOperator(task_id='upload-aix-bot-02',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_02',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_02 = PythonOperator(task_id='trigger-aix-bot-02',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_02',
                                                       'challenge': challenge['name']})

        # AIX BOT 03
        upload_bot_03 = PythonOperator(task_id='upload-aix-bot-03',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_03',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_03 = PythonOperator(task_id='trigger-aix-bot-03',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_03',
                                                       'challenge': challenge['name']})

        # AIX BOT 04
        upload_bot_04 = PythonOperator(task_id='upload-aix-bot-04',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_04',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_04 = PythonOperator(task_id='trigger-aix-bot-04',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_04',
                                                       'challenge': challenge['name']})

        # AIX BOT 05
        upload_bot_05 = PythonOperator(task_id='upload-aix-bot-05',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_05',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_05 = PythonOperator(task_id='trigger-aix-bot-05',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_05',
                                                       'challenge': challenge['name']})

        # AIX BOT 06
        upload_bot_06 = PythonOperator(task_id='upload-aix-bot-06',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_06',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_06 = PythonOperator(task_id='trigger-aix-bot-06',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_06',
                                                       'challenge': challenge['name']})

        # AIX BOT 07
        upload_bot_07 = PythonOperator(task_id='upload-aix-bot-07',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_07',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_07 = PythonOperator(task_id='trigger-aix-bot-07',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_07',
                                                       'challenge': challenge['name']})

        # AIX BOT 08
        upload_bot_08 = PythonOperator(task_id='upload-aix-bot-08',
                                       provide_context=True,
                                       python_callable=submit_bot_code,
                                       op_kwargs={'bot_name': 'bot_aix_08',
                                                  'challenge': challenge['name']})

        trigger_aix_bot_08 = PythonOperator(task_id='trigger-aix-bot-08',
                                            provide_context=True,
                                            python_callable=bot_trigger,
                                            op_kwargs={'bot_name': 'bot_aix_08',
                                                       'challenge': challenge['name']})

        # ACTIVATE SUBMISSIONS
        activate_submissions = PythonOperator(task_id='activate-submissions',
                                              provide_context=True,
                                              python_callable=activate_bot_submissions,
                                              op_kwargs={'bot_names': ['bot_lgbm', 'bot_dummy',
                                                                       'bot_sklearn', 'bot_steal',
                                                                       'bot_aix_01', 'bot_aix_02',
                                                                       'bot_aix_03', 'bot_aix_04',
                                                                       'bot_aix_05', 'bot_aix_06',
                                                                       'bot_aix_07', 'bot_aix_08'],
                                                         'challenge': challenge['name']})

        # DEPENDENCIES
        upload_sklearn_bot >> trigger_sklearn_bot
        upload_dummy_bot >> trigger_dummy_bot
        upload_lgbm_bot >> trigger_lgbm_bot
        upload_steal_bot >> trigger_steal_bot
        upload_pytorch_bot >> trigger_pytorch_bot
        upload_bot_01 >> trigger_aix_bot_01
        upload_bot_02 >> trigger_aix_bot_02
        upload_bot_03 >> trigger_aix_bot_03
        upload_bot_04 >> trigger_aix_bot_04
        upload_bot_05 >> trigger_aix_bot_05
        upload_bot_06 >> trigger_aix_bot_06
        upload_bot_07 >> trigger_aix_bot_07
        upload_bot_08 >> trigger_aix_bot_08
        trigger_tasks = [trigger_sklearn_bot, trigger_dummy_bot, trigger_lgbm_bot,
                         trigger_steal_bot, trigger_pytorch_bot, trigger_aix_bot_01,
                         trigger_aix_bot_02, trigger_aix_bot_03, trigger_aix_bot_04,
                         trigger_aix_bot_05, trigger_aix_bot_06, trigger_aix_bot_07, trigger_aix_bot_08]
        trigger_tasks >> activate_submissions

        globals()[dag_id] = dag

"""Server-side training DAG definition"""
from yaml import safe_load
from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.python import PythonOperator, BranchPythonOperator
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")
from operators import VMShutdownSensorOperator
from globals import CHALLENGES
from callables import *

DAG_CONFIGURATION_KEYS = {"artifacts_gcs_path", "code_gcs_path", "data_gcs_path", "evaluation_gcs_path",
                          "logs_gcs_path", "project", "repo_gcs_path", "resource_suffix", "user_dataset",
                          "user_id", "zone", "dag_retries", "output_gcs_path", "challenge"}

default_args = {
    'owner': 'newco',
    'depends_on_past': False,
    'start_date': datetime.datetime(1900, 1, 1),  # airflow starts one schedule interval AFTER start_date
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=1)
}
for key, challenge in CHALLENGES.items():
    dag_id = f'{key}_inference_job'
    with DAG(dag_id, default_args=default_args, schedule_interval=None) as dag:
        try:
            with open('/root/airflow/dags/backend/config/inference.yaml', 'r') as f:
                config = safe_load(f)
        except FileNotFoundError:
            with open('./config/inference.yaml', 'r') as f:
                config = safe_load(f)

        # RETRIEVE PARAMETERS
        user_id = "{{ dag_run.conf['user_id'] }}"
        project = "{{ dag_run.conf['project'] }}"
        challenge_str = "{{ dag_run.conf['challenge'] }}"
        orchestration_sa = "{{ dag_run.conf['orchestration_sa'] }}"
        resource_suffix = "{{ dag_run.conf['resource_suffix'] }}"
        user_dataset = "{{ dag_run.conf['user_dataset'] }}"
        zone = "{{ dag_run.conf['zone'] }}"
        repo_gcs_path = "{{ dag_run.conf['repo_gcs_path'] }}"
        code_gcs_path = "{{ dag_run.conf['code_gcs_path'] }}"
        data_gcs_path = "{{ dag_run.conf['data_gcs_path'] }}"
        artifacts_gcs_path = "{{ dag_run.conf['artifacts_gcs_path'] }}"
        logs_gcs_path = "{{ dag_run.conf['logs_gcs_path'] }}"
        output_gcs_path = "{{ dag_run.conf['output_gcs_path'] }}"
        dag_retries = "{{ dag_run.conf['dag_retries'] }}"
        run_parameters_dict = {'user_id': user_id, 'project': project, 'resource_suffix': resource_suffix,
                               'user_dataset': user_dataset, 'zone': zone,
                               'repo_gcs_path': repo_gcs_path, 'code_gcs_path': code_gcs_path,
                               'data_gcs_path': data_gcs_path, 'artifacts_gcs_path': artifacts_gcs_path,
                               'logs_gcs_path': logs_gcs_path, 'output_gcs_path': output_gcs_path,
                               'dag_retries': dag_retries, 'challenge': challenge_str,
                               'orchestration_sa': orchestration_sa}

        # PUBLISH RUN PARAMETERS
        publish_parameters = PythonOperator(task_id='publish-run-parameters',
                                            python_callable=publish_run_parameters,
                                            op_kwargs={'run_dict': run_parameters_dict})

        # CLEAR USER DATASET
        clear_user_dataset = PythonOperator(task_id='clear-user-dataset', python_callable=bq_delete_data,
                                            provide_context=True, op_args=[project, user_dataset, []])

        # CREATE USER DISK
        create_user_disk = PythonOperator(task_id='create-user-disk',
                                          python_callable=create_disk,
                                          op_args=[config['project'], config['zone'],
                                                   config['task']['create_user_disk']['name'],
                                                   config['task']['create_user_disk']['size'],
                                                   config['task']['create_user_disk']['type']])

        # CREATE DISK-PREP + BQ EXECUTION VM
        create_disk_prep_vm = PythonOperator(task_id='create-disk-prep-vm',
                                             python_callable=create_instance,
                                             provide_context=True,
                                             op_args=[config['project'], config['zone'],
                                                      config['task']['create_disk_prep_vm']['name'],
                                                      config['task']['create_disk_prep_vm']['machine_type']],
                                             op_kwargs={"additional_disks": config['task']['create_disk_prep_vm'][
                                                 'additional_disks'],
                                                        "add_external_ip": config['task']['create_disk_prep_vm'][
                                                            'add_external_ip'],
                                                        "source_image": config['task']['create_disk_prep_vm'][
                                                            'source_image'],
                                                        "service_account": config['task']['create_disk_prep_vm'][
                                                            'service_account'],
                                                        "challenge": config['challenge'],
                                                        "challenge_dict": CHALLENGES})

        # FORMAT USER DISK
        format_user_disk = PythonOperator(task_id='format-user-disk',
                                          python_callable=run_gcloud,
                                          retries=3,
                                          op_args=[config['task']['format_user_disk']['cmd']])

        # MOUNT USER DISK
        mount_user_disk = PythonOperator(task_id='mount-user-disk', python_callable=run_gcloud,
                                         op_args=[config['task']['mount_user_disk']['cmd']])

        # SYNC REPO
        sync_repo = PythonOperator(task_id='sync-repo', python_callable=data_sync,
                                   provide_context=True, op_args=[config['task']['sync_repo']['cmd']])

        # SYNC CODE
        sync_code = PythonOperator(task_id='sync-code', python_callable=data_sync,
                                   provide_context=True, op_args=[config['task']['sync_code']['cmd']])

        # SYNC ARTIFACTS
        sync_artifacts = PythonOperator(task_id='sync-artifacts', python_callable=data_sync,
                                        provide_context=True, op_args=[config['task']['sync_artifacts']['cmd']])

        # UNZIP CODE
        unzip_code = PythonOperator(task_id='unzip-code', python_callable=run_gcloud,
                                    provide_context=True, op_args=[config['task']['unzip_code']['cmd']])

        # DETERMINE SQL EXECUTION
        sql_execution_branching = BranchPythonOperator(task_id='sql-branching', python_callable=sql_branching,
                                                       provide_context=True,
                                                       op_args=[config['task']['sql_execution_branching']['cmd']],
                                                       op_kwargs=config['task']['sql_execution_branching']['mode'])

        # BQ EXECUTION COMMAND
        bq_execution_inference = PythonOperator(task_id='bq-execution-inference', python_callable=bq_execution,
                                                provide_context=True,
                                                op_args=[config['task']['bq_execution_inference']['cmd']])

        # SYNC DATA FROM BQ TO GCS
        sync_inference_data_user_bq_gcs = PythonOperator(task_id='sync-inference-data-user-bq-gcs',
                                                         python_callable=bq_data_sync,
                                                         provide_context=True,
                                                         op_args=[config['project'], config['user_dataset'], [],
                                                                  config['data_gcs_path']])
        sync_inference_data_bq_gcs = PythonOperator(task_id='sync-inference-data-bq-gcs', python_callable=bq_data_sync,
                                                    provide_context=True,
                                                    # trigger_rule=TriggerRule.NONE_FAILED,
                                                    op_args=[config['project'], 'inference_layer',
                                                             [f"{config['project']}.inference_layer.d_inference"],
                                                             config['data_gcs_path']])

        # DELETE DATA FROM BQ
        delete_user_inference_data_bq = PythonOperator(task_id='delete-user-inference-data-bq',
                                                       python_callable=bq_delete_data,
                                                       provide_context=True,
                                                       op_args=[config['project'], config['user_dataset'], []])

        # SYNC DATA FROM GCS TO USER DISK
        sync_inference_data_gcs_disk = PythonOperator(task_id='sync-inference-data-gcs-disk', python_callable=data_sync,
                                                      trigger_rule=TriggerRule.ALL_DONE,
                                                      provide_context=True,
                                                      op_args=[config['task']['sync_inference_data_gcs_disk']['cmd']])

        # DELETE DATA FROM GCS
        delete_data_from_gcs_task = PythonOperator(task_id='delete-data-from-gcs', python_callable=delete_data_from_gcs,
                                                   provide_context=True, op_args=[config['data_gcs_path']])

        # STOP VM
        stop_disk_prep_vm = PythonOperator(task_id='stop-disk-prep-vm', python_callable=run_gcloud,
                                           trigger_rule=TriggerRule.ALL_DONE,
                                           op_args=[config['task']['stop_disk_prep_vm']['cmd']])

        # DELETE VM
        delete_disk_prep_vm = PythonOperator(task_id='delete-disk-prep-vm', python_callable=run_gcloud,
                                             op_args=[config['task']['delete_disk_prep_vm']['cmd']])

        # CREATE INFERENCE VAULT VM
        create_vault_vm = PythonOperator(task_id='create-vault-vm',
                                         python_callable=create_instance,
                                         provide_context=True,
                                         op_args=[config['project'],
                                                  config['zone'],
                                                  config['task']['create_vault_vm']['name'],
                                                  config['task']['create_vault_vm']['machine_type']],
                                         op_kwargs={
                                             "additional_disks": config['task']['create_vault_vm']['additional_disks'],
                                             "startup_script": config['task']['create_vault_vm']['startup_script'],
                                             "source_image": config['task']['create_vault_vm']['source_image'],
                                             "vault_network": config['task']['create_vault_vm']['vault_network'],
                                             "challenge": config['challenge'],
                                             "challenge_dict": CHALLENGES
                                             })

        # VM SENSOR
        wait_inference_vault_execution = VMShutdownSensorOperator(task_id='wait-inference-vault-execution',
                                                                  poke_interval=
                                                                  config['task']['wait_inference_vault_execution'][
                                                                      'poke_interval'],
                                                                  timeout=config['task']['wait_inference_vault_execution'][
                                                                      'timeout'],
                                                                  mode=config['task']['wait_inference_vault_execution'][
                                                                      'mode'],
                                                                  poke_kwargs={'instance_name': config['task'][
                                                                      'wait_inference_vault_execution']['name'],
                                                                               'zone': config['zone'],
                                                                               'project': config['project']})

        # DELETE VAULT VM
        delete_vault_vm = PythonOperator(task_id='delete-vault-vm',
                                         trigger_rule=TriggerRule.ALL_DONE,
                                         python_callable=run_gcloud,
                                         op_args=[config['task']['delete_vault_vm']['cmd']])

        # CREATE DATA EXTRACTION VM
        create_data_extraction_vm = PythonOperator(task_id='create-data-extraction-vm',
                                                   python_callable=create_instance,
                                                   provide_context=True,
                                                   op_args=[config['project'],
                                                            config['zone'],
                                                            config['task']['create_data_extraction_vm']['name'],
                                                            config['task']['create_data_extraction_vm']['machine_type']],
                                                   op_kwargs={
                                                       "additional_disks": config['task']['create_data_extraction_vm'][
                                                           'additional_disks'],
                                                       "add_external_ip": config['task']['create_data_extraction_vm'][
                                                           'add_external_ip'],
                                                       "service_account": config['task']['create_data_extraction_vm'][
                                                           'service_account'],
                                                       "challenge": config['challenge'],
                                                       "challenge_dict": CHALLENGES
                                                    })

        # MOUNT USER DISK TO DATA EXTRACTION VM
        data_extraction_mount_user_disk = PythonOperator(task_id='data-extraction-mount-user-disk',
                                                         python_callable=run_gcloud,
                                                         op_args=[config['task']['data_extraction_mount_user_disk']['cmd']])

        # SYNC OUTPUT TO GCS
        sync_output = PythonOperator(task_id='sync-output', python_callable=data_sync,
                                     provide_context=True, op_args=[config['task']['sync_output']['cmd']])

        # SYNC LOGS TO GCS
        sync_logs = PythonOperator(task_id='sync-logs', python_callable=data_sync,
                                   provide_context=True, op_args=[config['task']['sync_logs']['cmd']])

        # DELETE USER DISK
        delete_user_disk = PythonOperator(task_id='delete-user-disk', python_callable=run_gcloud,
                                          trigger_rule=TriggerRule.ALL_DONE,
                                          op_args=[config['task']['delete_user_disk']['cmd']])

        # DELETE DATA EXTRACTION VM
        delete_extraction_vm = PythonOperator(task_id='delete-extraction-vm', python_callable=run_gcloud,
                                              trigger_rule=TriggerRule.ALL_DONE,
                                              op_args=[config['task']['delete_extraction_vm']['cmd']])

        # GATHER RESOURCE USAGE INFORMATION
        task_instances = dag.get_task_instances()
        get_usage_info = PythonOperator(task_id='get-usage-info',
                                        provide_context=True,
                                        retries=3,
                                        python_callable=get_usage_information,
                                        trigger_rule=TriggerRule.ALL_DONE,
                                        op_args=['inference', task_instances, config['user_id']])

        # MANAGE ZONE RESOURCE POOL EXHAUSTION
        manage_zonal_exhaustion = PythonOperator(task_id='manage-zonal-exhaustion',
                                                 provide_context=True,
                                                 retries=3,
                                                 python_callable=manage_zone_resource_pool_exhaustion,
                                                 trigger_rule=TriggerRule.ALL_DONE,
                                                 op_kwargs={'parent_tasks': ['create-disk-prep-vm',
                                                                             'create-vault-vm',
                                                                             'create-data-extraction-vm'],
                                                            'dag_name': f"{challenge['name']}_inference_job",
                                                            'dag_configuration_keys': DAG_CONFIGURATION_KEYS,
                                                            'max_dag_retries': config['max_dag_retries'],
                                                            'challenge_dict': challenge})

        # DEPENDENCIES - use lists to set batches of dependencies
        create_user_disk >> create_disk_prep_vm >> format_user_disk >> mount_user_disk
        mount_user_disk >> sync_repo >> stop_disk_prep_vm
        mount_user_disk >> sync_code >> unzip_code
        mount_user_disk >> sync_artifacts >> stop_disk_prep_vm
        unzip_code >> sql_execution_branching
        sql_execution_branching >> bq_execution_inference
        sql_execution_branching >> sync_inference_data_bq_gcs

        # BQ default flow
        sync_inference_data_bq_gcs >> sync_inference_data_gcs_disk >> stop_disk_prep_vm
        sync_inference_data_gcs_disk >> delete_data_from_gcs_task

        # BQ execution train
        bq_execution_inference >> sync_inference_data_user_bq_gcs >> sync_inference_data_gcs_disk >> delete_data_from_gcs_task
        sync_inference_data_user_bq_gcs >> delete_user_inference_data_bq

        stop_disk_prep_vm >> delete_disk_prep_vm

        # Vault
        delete_disk_prep_vm >> create_vault_vm >> wait_inference_vault_execution >> delete_vault_vm
        delete_vault_vm >> create_data_extraction_vm
        wait_inference_vault_execution >> create_data_extraction_vm

        # EVAL
        create_data_extraction_vm >> data_extraction_mount_user_disk >> [sync_output, sync_logs]
        [sync_output, sync_logs] >> delete_extraction_vm >> delete_user_disk
        delete_user_disk >> get_usage_info

        # ZONAL EXHAUSTION
        [create_disk_prep_vm, create_vault_vm, create_data_extraction_vm] >> manage_zonal_exhaustion

        globals()[dag_id] = dag

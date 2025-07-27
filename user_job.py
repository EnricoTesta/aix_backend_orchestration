"""Server-side training DAG definition"""
from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.python import PythonOperator, BranchPythonOperator
import sys

sys.path.insert(0, "/root/airflow/dags/backend/")
from operators import VMShutdownSensorOperator
from callables import *
from globals import CHALLENGES

DAG_CONFIGURATION_KEYS = {"artifacts_gcs_path", "code_gcs_path", "data_gcs_path", "evaluation_gcs_path",
                          "logs_gcs_path", "project", "repo_gcs_path", "resource_suffix", "user_dataset",
                          "user_id", "zone", "dag_retries", "output_gcs_path", "challenge"}

DEPLOYMENT_TYPE = os.getenv('AIRFLOW_ENV')
if DEPLOYMENT_TYPE is None:
    ORCHESTRATION_SA = "airflow-prod-sa"
elif DEPLOYMENT_TYPE == 'DEV':
    ORCHESTRATION_SA = "airflow-dev-sa"
else:
    raise ValueError(f"Unknown deployment {DEPLOYMENT_TYPE}")

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

TRAIN_DATASET = "training_layer"
EVAL_DATASET = "evaluation_layer"

for key, challenge in CHALLENGES.items():

    dag_id = f'{key}_user_job'
    with DAG(dag_id, default_args=default_args, schedule_interval=None) as dag:
        # RETRIEVE PARAMETERS
        user_id = "{{ dag_run.conf['user_id'] }}"
        project = "{{ dag_run.conf['project'] }}"
        resource_suffix = "{{ dag_run.conf['resource_suffix'] }}"
        user_dataset = "{{ dag_run.conf['user_dataset'] }}"
        challenge_to_be_removed = "{{ dag_run.conf['challenge'] }}"
        zone = "{{ dag_run.conf['zone'] }}"
        repo_gcs_path = "{{ dag_run.conf['repo_gcs_path'] }}"
        code_gcs_path = "{{ dag_run.conf['code_gcs_path'] }}"
        logs_gcs_path = "{{ dag_run.conf['logs_gcs_path'] }}"
        data_gcs_path = "{{ dag_run.conf['data_gcs_path'] }}"
        artifacts_gcs_path = "{{ dag_run.conf['artifacts_gcs_path'] }}"
        evaluation_gcs_path = "{{ dag_run.conf['evaluation_gcs_path'] }}"
        dag_retries = "{{ dag_run.conf['dag_retries'] }}"
        run_parameters_dict = {'user_id': user_id, 'project': project, 'resource_suffix': resource_suffix,
                               'user_dataset': user_dataset, 'zone': zone,
                               'repo_gcs_path': repo_gcs_path, 'code_gcs_path': code_gcs_path,
                               'data_gcs_path': data_gcs_path, 'artifacts_gcs_path': artifacts_gcs_path,
                               'evaluation_gcs_path': evaluation_gcs_path, 'logs_gcs_path': logs_gcs_path,
                               'dag_retries': dag_retries, 'challenge': challenge_to_be_removed}

        # PUBLISH RUNNING JOB STATE
        publish_running_job = PythonOperator(task_id='publish-running-job',
                                             python_callable=publish_job_run,
                                             op_kwargs={'user_id': user_id, 'challenge': challenge['name']})

        # PUBLISH RUN PARAMETERS
        publish_parameters = PythonOperator(task_id='publish-run-parameters',
                                            python_callable=publish_run_parameters,
                                            op_kwargs={'run_dict': run_parameters_dict})

        # CLEAR USER DATASET
        clear_user_dataset = PythonOperator(task_id='clear-user-dataset', python_callable=bq_delete_data,
                                            provide_context=True, op_args=[project, user_dataset, []])

        # CREATE USER DISK
        cud_dict = {"name": f'udisk-{resource_suffix}',
                    "project": project,
                    "size": 10,
                    "type": f'projects/{project}/zones/{zone}/diskTypes/pd-ssd',
                    # pd-standard, pd-balanced, pd-ssd, pd-extreme
                    "zone": zone}
        create_user_disk = PythonOperator(task_id='create-user-disk',
                                          python_callable=create_disk,
                                          op_args=[project, zone, f'udisk-{resource_suffix}', cud_dict['size'],
                                                   cud_dict['type']])

        # CREATE DISK-PREP + BQ EXECUTION VM
        create_disk_prep_vm = PythonOperator(task_id='create-disk-prep-vm',
                                             python_callable=create_instance,
                                             provide_context=True,
                                             op_args=[project, zone, f'disk-prep-vm-{resource_suffix}', 'e2-micro'],
                                             op_kwargs={"additional_disks": [{"device_name": f'udisk-{resource_suffix}',
                                                                              "url": f'projects/{project}/zones/{zone}/disks/udisk-{resource_suffix}',
                                                                              "mode": 'rw'}],
                                                        "add_external_ip": True,
                                                        "source_image": f"projects/aix-backend-prod/global/images/codebox-boot-image",
                                                        "service_account": True,
                                                        "challenge_dict": CHALLENGES,
                                                        "challenge": challenge['name']})

        # FORMAT USER DISK
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@disk-prep-vm-{resource_suffix} --zone={zone} --project={project} --quiet --command='sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb'"
        format_user_disk = PythonOperator(task_id='format-user-disk',
                                          python_callable=run_gcloud,
                                          retries=3,
                                          op_args=[cmd])

        # MOUNT USER DISK
        mud_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                    "project": project,
                    "command": "sudo mkdir -p /mnt/user-disk && \
                                sudo mount -o discard,defaults /dev/sdb /mnt/user-disk && \
                                sudo mkdir /mnt/user-disk/code/ && \
                                sudo mkdir /mnt/user-disk/repo/ && \
                                sudo mkdir /mnt/user-disk/input/ && \
                                sudo mkdir /mnt/user-disk/eval/ && \
                                sudo mkdir /mnt/user-disk/eval/data && \
                                sudo mkdir /mnt/user-disk/eval/output && \
                                sudo mkdir /mnt/user-disk/output/ && \
                                sudo mkdir /mnt/user-disk/logs/ && \
                                sudo chmod -R 777 /mnt/user-disk",
                    "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{mud_dict['instance']} --zone={zone} --project={project} --quiet --command='{mud_dict['command']}'"
        mount_user_disk = PythonOperator(task_id='mount-user-disk', python_callable=run_gcloud, op_args=[cmd])

        # UPDATE REPO
        update_repo_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                            "project": project,
                            "command": f"python /codebox/repo.py --remote-repo-bucket={COMMON['pypi_repo_bucket_name']}"
                                       f" --remote-requirement-directory={code_gcs_path}",
                            "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{update_repo_dict['instance']} --zone={zone} --project={project} --quiet --command='{update_repo_dict['command']}'"
        update_repo = PythonOperator(task_id='update-repo', retries=3, python_callable=run_gcloud, provide_context=True,
                                     op_args=[cmd])

        # SYNC REPO
        sync_repo_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                          "project": project,
                          "command": f'gsutil -m rsync -r {repo_gcs_path} /mnt/user-disk/repo/',
                          "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sync_repo_dict['instance']} --zone={zone} --project={project} --quiet --command='{sync_repo_dict['command']}'"
        sync_repo = PythonOperator(task_id='sync-repo', retries=3, python_callable=data_sync, provide_context=True,
                                   op_args=[cmd])

        # SYNC CODE
        sync_code_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                          "project": project,
                          "command": f'gsutil -m rsync -r {code_gcs_path} /mnt/user-disk/code/',
                          "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sync_code_dict['instance']} --zone={zone} --project={project} --quiet --command='{sync_code_dict['command']}'"
        sync_code = PythonOperator(task_id='sync-code', retries=3, python_callable=data_sync, provide_context=True,
                                   op_args=[cmd])

        # UNZIP CODE
        unzip_code_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                           "project": project,
                           "command": f'unzip /mnt/user-disk/code/*.zip -d /mnt/user-disk/code/',
                           "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{unzip_code_dict['instance']} --zone={zone} --project={project} --quiet --command='{unzip_code_dict['command']}'"
        unzip_code = PythonOperator(task_id='unzip-code', python_callable=run_gcloud, provide_context=True, op_args=[cmd])

        # DETERMINE SQL EXECUTION
        sql_execution_branching_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                                        "project": project,
                                        "command": f'cd /mnt/user-disk/code/ && ls -d */',
                                        # list all directories in current path
                                        "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sql_execution_branching_dict['instance']} --zone={zone} --project={project} --quiet --command='{sql_execution_branching_dict['command']}'"
        sql_execution_branching = BranchPythonOperator(task_id='sql-branching', python_callable=sql_branching,
                                                       provide_context=True, op_args=[cmd])

        # BQ EXECUTION COMMAND
        bq_exec_train_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                              "project": project,
                              "command": f'python /codebox/sql_execution.py --project={project} --source-dataset={TRAIN_DATASET} --user-dataset={user_dataset} --custom-code-path=/mnt/user-disk/code/',
                              "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{bq_exec_train_dict['instance']} --zone={zone} --project={project} --quiet --command='{bq_exec_train_dict['command']}'"
        bq_execution_train = PythonOperator(task_id='bq-execution-train', python_callable=bq_execution,
                                            provide_context=True, op_args=[cmd])

        bq_exec_eval_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                             "project": project,
                             "command": f'python /codebox/sql_execution.py --project={project} --source-dataset={EVAL_DATASET} --user-dataset={user_dataset} --custom-code-path=/mnt/user-disk/code/',
                             "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{bq_exec_eval_dict['instance']} --zone={zone} --project={project} --quiet --command='{bq_exec_eval_dict['command']}'"
        bq_execution_eval = PythonOperator(task_id='bq-execution-eval', python_callable=bq_execution, provide_context=True,
                                           op_args=[cmd])

        # SYNC DATA FROM BQ TO GCS
        train_data_gcs_path = f"{data_gcs_path}train"
        sync_train_data_user_bq_gcs = PythonOperator(task_id='sync-train-data-user-bq-gcs', retries=3,
                                                     python_callable=bq_data_sync, provide_context=True,
                                                     op_args=[project, user_dataset, [], train_data_gcs_path, True])
        sync_train_data_bq_gcs = PythonOperator(task_id='sync-train-data-bq-gcs', retries=3, python_callable=bq_data_sync,
                                                provide_context=True, trigger_rule=TriggerRule.NONE_FAILED,
                                                op_args=[project, 'training_layer',
                                                         [f"{project}.training_layer.d_train"], train_data_gcs_path,
                                                         True])

        eval_data_gcs_path = f"{data_gcs_path}eval"
        sync_eval_data_user_bq_gcs = PythonOperator(task_id='sync-eval-data-user-bq-gcs', retries=3,
                                                    python_callable=bq_data_sync, provide_context=True,
                                                    op_args=[project, user_dataset, [], eval_data_gcs_path, True])
        sync_eval_data_bq_gcs = PythonOperator(task_id='sync-eval-data-bq-gcs', retries=3, python_callable=bq_data_sync,
                                               provide_context=True, trigger_rule=TriggerRule.NONE_FAILED,
                                               op_args=[project, 'evaluation_layer',
                                                        [f"{project}.evaluation_layer.d_holdout"], eval_data_gcs_path,
                                                        True])

        # DELETE DATA FROM BQ
        delete_user_train_data_bq = PythonOperator(task_id='delete-user-train-data-bq', retries=3,
                                                   python_callable=bq_delete_data, provide_context=True,
                                                   op_args=[project, user_dataset, []])
        delete_user_eval_data_bq = PythonOperator(task_id='delete-user-eval-data-bq', retries=3,
                                                  python_callable=bq_delete_data, provide_context=True,
                                                  op_args=[project, user_dataset, []])

        # SYNC DATA FROM GCS TO USER DISK
        sync_train_data_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                                "project": project,
                                "command": f'gsutil -m rsync -r {train_data_gcs_path} /mnt/user-disk/input/',
                                "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sync_train_data_dict['instance']} --zone={zone} --project={project} --quiet --command='{sync_train_data_dict['command']}'"
        sync_train_data_gcs_disk = PythonOperator(task_id='sync-train-data-gcs-disk', retries=3, python_callable=data_sync,
                                                  trigger_rule=TriggerRule.ALL_DONE, provide_context=True, op_args=[cmd])

        sync_eval_data_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                               "project": project,
                               "command": f'gsutil -m rsync -r {eval_data_gcs_path} /mnt/user-disk/eval/data/',
                               "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sync_eval_data_dict['instance']} --zone={zone} --project={project} --quiet --command='{sync_eval_data_dict['command']}'"
        sync_eval_data_gcs_disk = PythonOperator(task_id='sync-eval-data-gcs-disk', retries=3, python_callable=data_sync,
                                                 trigger_rule=TriggerRule.ALL_DONE, provide_context=True, op_args=[cmd])

        # DELETE DATA FROM GCS
        delete_data_from_gcs_task = PythonOperator(task_id='delete-data-from-gcs', retries=3,
                                                   python_callable=delete_data_from_gcs, provide_context=True,
                                                   op_args=[data_gcs_path])

        # STOP VM
        stop_vm_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                        "project": project,
                        "zone": zone}
        cmd = f"gcloud compute instances stop {stop_vm_dict['instance']} --zone={zone} --project={project} --quiet"
        stop_disk_prep_vm = PythonOperator(task_id='stop-disk-prep-vm', python_callable=run_gcloud,
                                           trigger_rule=TriggerRule.ALL_DONE, op_args=[cmd])

        # DELETE VM
        delete_vm_dict = {"instance": f'disk-prep-vm-{resource_suffix}',
                          "project": project,
                          "zone": zone}
        cmd = f"gcloud compute instances delete {delete_vm_dict['instance']} --zone={zone} --project={project} --quiet"
        delete_disk_prep_vm = PythonOperator(task_id='delete-disk-prep-vm', python_callable=run_gcloud, op_args=[cmd])

        # CREATE TRAIN VAULT VM
        vault_vm_disks = [{"device_name": f'udisk-{resource_suffix}',
                           "url": f'projects/{project}/zones/{zone}/disks/udisk-{resource_suffix}',
                           "mode": 'rw'}]
        # To check script results: sudo journalctl -u google-startup-scripts.service -f
        start_up_script = "#!/bin/bash \n" \
                          "sudo mount -o discard,defaults /dev/sdb /user_workarea && sudo chmod -R 777 /user_workarea \n" \
                          "sudo python /codebox/codebox.py --config-file-uri /codebox/config/process_config.yaml"
        vault_source_image = "projects/aix-backend-prod/global/images/codebox-boot-image"
        vault_vm = PythonOperator(task_id='create-vault-vm',
                                  python_callable=create_instance,
                                  provide_context=True,
                                  op_args=[project, zone, f'vault-vm-{resource_suffix}', 'n2-standard-4'],
                                  op_kwargs={"additional_disks": vault_vm_disks,
                                             "startup_script": start_up_script,
                                             "source_image": vault_source_image,
                                             "vault_network": True,
                                             "challenge_dict": CHALLENGES,
                                             "challenge": challenge['name']
                                             })

        # CREATE EVAL VAULT VM
        eval_vault_vm_disks = [{"device_name": f'udisk-{resource_suffix}',
                                "url": f'projects/{project}/zones/{zone}/disks/udisk-{resource_suffix}',
                                "mode": 'rw'}]
        # To check script results: sudo journalctl -u google-startup-scripts.service -f
        eval_start_up_script = "#!/bin/bash \n" \
                               "sudo mount -o discard,defaults /dev/sdb /user_workarea && sudo chmod -R 777 /user_workarea \n" \
                               "sudo gsutil -m rsync -r /user_workarea/output/ /user_workarea/eval/ \n" \
                               "sudo python /codebox/codebox.py --config-file-uri /codebox/config/eval_config.yaml"
        vault_source_image = "projects/aix-backend-prod/global/images/codebox-boot-image"
        eval_vault_vm = PythonOperator(task_id='create-eval-vault-vm',
                                       python_callable=create_instance,
                                       provide_context=True,
                                       op_args=[project, zone, f'eval-vault-vm-{resource_suffix}', 'n1-standard-2'],
                                       op_kwargs={"additional_disks": eval_vault_vm_disks,
                                                  "startup_script": eval_start_up_script,
                                                  "source_image": vault_source_image,
                                                  "vault_network": True,
                                                  "challenge_dict": CHALLENGES,
                                                  "challenge": challenge['name']
                                                  })

        # VM SENSOR
        poke_dict = {'instance_name': f'vault-vm-{resource_suffix}', 'zone': zone, 'project': project}
        wait_vault_execution = VMShutdownSensorOperator(task_id='wait-vault-execution',
                                                        poke_interval=180,
                                                        retries=0,
                                                        timeout=3600 * 6,
                                                        mode='reschedule',
                                                        poke_kwargs=poke_dict)

        eval_poke_dict = {'instance_name': f'eval-vault-vm-{resource_suffix}', 'zone': zone, 'project': project}
        wait_eval_vault_execution = VMShutdownSensorOperator(task_id='wait-eval-vault-execution',
                                                             poke_interval=120,
                                                             retries=0,
                                                             timeout=600,
                                                             mode='reschedule',
                                                             poke_kwargs=eval_poke_dict)

        # DELETE VAULT VM
        delete_vault_vm_dict = {"instance": f'vault-vm-{resource_suffix}',
                                "project": project,
                                "zone": zone}
        cmd = f"gcloud compute instances delete {delete_vault_vm_dict['instance']} --zone={zone} --project={project} --quiet"
        delete_vault_vm = PythonOperator(task_id='delete-vault-vm', trigger_rule=TriggerRule.ALL_DONE,
                                         python_callable=run_gcloud, op_args=[cmd])

        delete_eval_vault_vm_dict = {"instance": f'eval-vault-vm-{resource_suffix}',
                                     "project": project,
                                     "zone": zone}
        cmd = f"gcloud compute instances delete {delete_eval_vault_vm_dict['instance']} --zone={zone} --project={project} --quiet"
        delete_eval_vault_vm = PythonOperator(task_id='delete-eval-vault-vm', trigger_rule=TriggerRule.ALL_DONE,
                                              python_callable=run_gcloud, op_args=[cmd])

        # CREATE DATA EXTRACTION VM
        create_data_extraction_vm = PythonOperator(task_id='create-data-extraction-vm',
                                                   python_callable=create_instance,
                                                   provide_context=True,
                                                   trigger_rule=TriggerRule.ALL_DONE,
                                                   op_args=[project, zone, f'data-extraction-vm-{resource_suffix}',
                                                            'n1-standard-1'],
                                                   op_kwargs={
                                                       "additional_disks": [{"device_name": f'udisk-{resource_suffix}',
                                                                             "url": f'projects/{project}/zones/{zone}/disks/udisk-{resource_suffix}',
                                                                             "mode": 'ro'}],
                                                       "add_external_ip": True,
                                                       "service_account": True,
                                                       "challenge_dict": CHALLENGES,
                                                       "challenge": challenge['name']
                                                   })

        # MOUNT USER DISK TO DATA EXTRACTION VM
        de_mud_dict = {"instance": f'data-extraction-vm-{resource_suffix}',
                       "project": project,
                       "command": 'sudo mkdir -p /user-disk && sudo mount -o discard,defaults /dev/sdb /user-disk && sudo chmod -R 555 /user-disk',
                       "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{de_mud_dict['instance']} --zone={zone} --project={project} --quiet --command='{de_mud_dict['command']}'"
        data_extraction_mount_user_disk = PythonOperator(task_id='data-extraction-mount-user-disk',
                                                         python_callable=run_gcloud, op_args=[cmd])

        # SYNC OUTPUT TO GCS
        sync_output_dict = {"instance": f'data-extraction-vm-{resource_suffix}',
                            "project": project,
                            "command": f'gsutil -m rsync -r /user-disk/output {artifacts_gcs_path}',
                            "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sync_output_dict['instance']} --zone={zone} --project={project} --quiet --command='{sync_output_dict['command']}'"
        sync_output = PythonOperator(task_id='sync-output', retries=3, python_callable=data_sync, provide_context=True,
                                     op_args=[cmd])

        # SYNC LOGS TO GCS
        sync_log_dict = {"instance": f'data-extraction-vm-{resource_suffix}',
                         "project": project,
                         "command": f'gsutil -m rsync -r /user-disk/logs {logs_gcs_path}',  # currently, matches user bucket
                         "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sync_log_dict['instance']} --zone={zone} --project={project} --quiet --command='{sync_log_dict['command']}'"
        sync_logs = PythonOperator(task_id='sync-logs', retries=3, python_callable=data_sync, provide_context=True,
                                   op_args=[cmd])

        # SYNC EVAL TO GCS
        sync_eval_dict = {"instance": f'data-extraction-vm-{resource_suffix}',
                          "project": project,
                          "command": f'gsutil -m rsync -r /user-disk/eval/output {evaluation_gcs_path}',
                          "zone": zone}
        cmd = f"gcloud compute ssh {ORCHESTRATION_SA}@{sync_eval_dict['instance']} --zone={zone} --project={project} --quiet --command='{sync_eval_dict['command']}'"
        sync_eval = PythonOperator(task_id='sync-eval', retries=3, python_callable=data_sync, provide_context=True,
                                   op_args=[cmd])

        # SYNC EVAL TO BQ
        bq_eval_upload_dict = {"project": project,
                               "dataset": user_dataset,
                               "table": "eval_predictions",
                               "file_uri": f"{evaluation_gcs_path}predictions.csv"}
        bq_eval_upload = PythonOperator(task_id='bq-eval-upload', retries=3, python_callable=bq_upload_from_gcs,
                                        provide_context=True, op_kwargs=bq_eval_upload_dict)

        # MODEL EVALUATION (local)
        model_evaluation_dict = {"challenge": challenge['name'], "dataset": user_dataset, "user_id": user_id}
        model_evaluation = PythonOperator(task_id='model-evaluation', python_callable=compute_and_send_metrics,
                                          provide_context=True, op_kwargs=model_evaluation_dict)

        # DELETE BQ EVALUATION TABLES
        bq_delete_eval_task = PythonOperator(task_id='bq-delete-eval', retries=3, python_callable=bq_delete_data,
                                             provide_context=True, op_args=[project, user_dataset, []])

        # DELETE USER DISK
        delete_user_disk_dict = {"disk": f'udisk-{resource_suffix}',
                                 "project": project,
                                 "zone": zone}
        cmd = f"gcloud compute disks delete {delete_user_disk_dict['disk']} --zone={zone} --project={project} --quiet"
        delete_user_disk = PythonOperator(task_id='delete-user-disk',
                                          python_callable=run_gcloud,
                                          trigger_rule=TriggerRule.ALL_DONE,
                                          op_args=[cmd])

        # DELETE DATA EXTRACTION VM
        delete_extraction_vm_dict = {"instance": f'data-extraction-vm-{resource_suffix}',
                                     "project": project,
                                     "zone": zone}
        cmd = f"gcloud compute instances delete {delete_extraction_vm_dict['instance']} --zone={zone} --project={project} --quiet"
        delete_extraction_vm = PythonOperator(task_id='delete-extraction-vm',
                                              trigger_rule=TriggerRule.ALL_DONE,
                                              python_callable=run_gcloud,
                                              op_args=[cmd])

        # GATHER RESOURCE USAGE INFORMATION
        task_instances = dag.get_task_instances()
        get_usage_info = PythonOperator(task_id='get-usage-info',
                                        provide_context=True,
                                        python_callable=get_usage_information,
                                        retries=3,
                                        trigger_rule=TriggerRule.ALL_DONE,
                                        op_args=['user', task_instances, user_id])

        # ARTIFACT QUALITY ASSURANCE
        quality_assurance = PythonOperator(task_id='artifact-quality-assurance',
                                           provide_context=True,
                                           python_callable=artifact_quality_assurance,
                                           retries=1,
                                           trigger_rule=TriggerRule.ALL_DONE)

        # DELETE PUBLISH JOB RUN
        delete_publish_running_job = PythonOperator(task_id='delete-publish-running-job',
                                                    python_callable=delete_publish_job_run,
                                                    trigger_rule=TriggerRule.ALL_DONE,
                                                    op_kwargs={'user_id': user_id, 'challenge': challenge['name']})

        email_notification = PythonOperator(task_id='email-notification',
                                            python_callable=notify_via_email,
                                            trigger_rule=TriggerRule.ALL_DONE,
                                            op_kwargs={'user_id': user_id,
                                                       'dag': f"{challenge['name']}_user_job",
                                                       'task_instance_list': task_instances,
                                                       'zonal_exhaustion_task_list': ['create-disk-prep-vm',
                                                                                      'vault-vm',
                                                                                      'eval-vault-vm',
                                                                                      'create-data-extraction-vm'],
                                                       'challenge': challenge['display_name']})

        # MANAGE ZONE RESOURCE POOL EXHAUSTION
        manage_zonal_exhaustion = PythonOperator(task_id='manage-zonal-exhaustion',
                                                 provide_context=True,
                                                 retries=3,
                                                 python_callable=manage_zone_resource_pool_exhaustion,
                                                 trigger_rule=TriggerRule.ALL_DONE,
                                                 op_kwargs={'parent_tasks': ['create-disk-prep-vm',
                                                                             'create-vault-vm',
                                                                             'create-eval-vault-vm',
                                                                             'create-data-extraction-vm'],
                                                            'dag_name': f"{challenge['name']}_user_job",
                                                            'dag_configuration_keys': DAG_CONFIGURATION_KEYS,
                                                            'challenge_dict': challenge,
                                                            'max_dag_retries': 3})

        # DEPENDENCIES - use lists to set batches of dependencies
        create_user_disk >> create_disk_prep_vm >> format_user_disk >> mount_user_disk
        mount_user_disk >> sync_repo >> stop_disk_prep_vm
        mount_user_disk >> sync_code >> unzip_code
        unzip_code >> sql_execution_branching
        sql_execution_branching >> bq_execution_train
        sql_execution_branching >> sync_train_data_bq_gcs
        sql_execution_branching >> sync_eval_data_bq_gcs

        # Update repo
        create_disk_prep_vm >> update_repo >> sync_repo

        # BQ default flow
        sync_train_data_bq_gcs >> sync_train_data_gcs_disk >> stop_disk_prep_vm
        sync_eval_data_bq_gcs >> sync_eval_data_gcs_disk >> stop_disk_prep_vm

        # BQ execution train
        bq_execution_train >> sync_train_data_user_bq_gcs >> sync_train_data_gcs_disk >> delete_data_from_gcs_task
        sync_train_data_user_bq_gcs >> delete_user_train_data_bq

        # BQ execution eval
        delete_user_train_data_bq >> bq_execution_eval >> sync_eval_data_user_bq_gcs >> delete_user_eval_data_bq
        bq_execution_eval >> sync_eval_data_user_bq_gcs >> sync_eval_data_gcs_disk
        sync_eval_data_gcs_disk >> delete_data_from_gcs_task

        stop_disk_prep_vm >> delete_disk_prep_vm

        # VAULTS
        delete_disk_prep_vm >> vault_vm >> wait_vault_execution >> delete_vault_vm
        wait_vault_execution >> eval_vault_vm
        delete_vault_vm >> eval_vault_vm >> wait_eval_vault_execution >> delete_eval_vault_vm
        wait_eval_vault_execution >> create_data_extraction_vm
        delete_eval_vault_vm >> create_data_extraction_vm

        # EVAL
        create_data_extraction_vm >> data_extraction_mount_user_disk >> sync_output
        data_extraction_mount_user_disk >> sync_eval
        data_extraction_mount_user_disk >> sync_logs
        sync_output >> bq_eval_upload >> model_evaluation >> bq_delete_eval_task
        sync_output >> delete_extraction_vm >> delete_user_disk
        bq_delete_eval_task >> get_usage_info
        delete_user_disk >> get_usage_info

        # WRAP UP
        get_usage_info >> [delete_publish_running_job, quality_assurance] >> email_notification

        # ZONAL EXHAUSTION
        [create_disk_prep_vm, vault_vm, eval_vault_vm, create_data_extraction_vm] >> manage_zonal_exhaustion

        globals()[dag_id] = dag


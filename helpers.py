"""
Helper functions. These functions are called by functions in callables.py, Airflow-ready wrappers.
"""

import datetime
from math import ceil
from yaml import safe_load
import psycopg2
import pathlib
import string
from random import choices
from tempfile import TemporaryDirectory
import subprocess
import os
import re
import sys
from logging import getLogger
from random import choice
from numpy import dot, ones
from json import dumps, dump
from google.cloud import bigquery, storage
from scipy.optimize import minimize
from sklearn.metrics import log_loss
from pandas import read_csv
import google.cloud.compute_v1 as compute_v1
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Template

helpers_logger = getLogger('Helpers_Logger')

with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'db/db.yaml'), 'r') as f:
    DB = safe_load(f)

with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'config/common.yaml'), 'r') as f:
    COMMON = safe_load(f)


def get_db_conn():
    return psycopg2.connect(host=DB['host'], database=DB['database'], user=DB['user'], password=DB['password'])


def run_query(query):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


def run_insert_statement(insert_statement):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(insert_statement)
    conn.commit()
    cur.close()
    conn.close()


def list2dbstr(l):
    s = "("
    for item in l:
        clean_item = item
        if isinstance(item, datetime.datetime):
            clean_item = str(item)
        elif isinstance(item, datetime.timedelta):
            clean_item = ceil(item.total_seconds())

        if isinstance(clean_item, str) and clean_item != 'NULL':
            s += "\'" + clean_item + "\', "
        else:
            s += str(clean_item) + ", "
    return s[0:-2] + ")"


def update_exhausted_zones(zones):
    with TemporaryDirectory() as tmp:
        for zone in zones:
            with open(os.path.join(tmp, zone), 'w') as f:
                f.write("")

        cmd = f"gsutil rsync -r {tmp} gs://{COMMON['zonal_exhaustion_bucket_name']}"
        subprocess.run(cmd, shell=True)


def choose_compute_zone():
    storage_client = storage.Client(project=COMMON['backend_project_name'])
    exhausted_zones = [blob.name for blob in
                       list(storage_client.list_blobs(bucket_or_name=COMMON['zonal_exhaustion_bucket_name']))]

    if exhausted_zones:
        eligible_zones = list(set(COMMON['compute_zones']) - set(exhausted_zones))
    else:
        eligible_zones = COMMON['compute_zones']

    return choice(eligible_zones)


def regenerate_dag_config(task_instance, dag_configuration_keys, choose_new_compute_zone=False):

    # Pull DAG configuration
    conf = {}
    for item in dag_configuration_keys:
        if item == 'dag_retries':
            conf[item] = int(task_instance.xcom_pull(task_ids='publish-run-parameters', key=item))
        else:
            conf[item] = task_instance.xcom_pull(task_ids='publish-run-parameters', key=item)

    if choose_new_compute_zone:
        conf['zone'] = choose_compute_zone()
        print(f"New compute zone: {conf['zone']}")

    if conf['dag_retries']:
        conf['dag_retries'] += 1
    else:
        conf['dag_retries'] = 1
    print(f"Dag retries set to {conf['dag_retries']}")

    # Change resource random suffix. Useful because sometimes new resources are generated before old ones are destroyed.
    conf['resource_suffix'] = conf['resource_suffix'][0:-5] +\
                              ''.join(choices(string.ascii_lowercase + string.digits, k=5))

    return conf

def get_user_dataset(user_uid):
    query_statement = "select dataset_id from public.user_registry where user_id = \'" + user_uid + "\'"
    results = run_query(query_statement)
    return results[0][0]


def get_user_bucket(user_id, return_users=False):
    if isinstance(user_id, list):
        sql_str = ''
        for item in user_id:
            sql_str += f"\'{item}\',"
        if return_users:
            query_statement = f"select bucket_id, user_id from user_registry where user_id in ({sql_str[0:-1]})"
        else:
            query_statement = f"select bucket_id from user_registry where user_id in ({sql_str[0:-1]})"
    else:
        query_statement = f"select bucket_id from user_registry where user_id=\'{user_id}\'"
    results = run_query(query_statement)
    if isinstance(user_id, list):
        return results
    return results[0][0]


def get_user_email(user_uid):
    query_statement = "select user_email from public.user_registry where user_id = \'" + user_uid + "\'"
    results = run_query(query_statement)
    return results[0][0]


def build_metamodel(predictions_df, target):
    D = len(predictions_df.columns)

    def my_objective_fun(w):
        return log_loss(target, dot(predictions_df, w), labels=[0, 1])

    x_0 = ones(D) / D
    bound = (0, 1)
    bounds = [bound for i in range(D)]
    constr_list = [{'type': 'eq', 'fun': lambda w: sum(w) - 1}]
    r = minimize(my_objective_fun, x0=x_0, bounds=bounds, constraints=constr_list)
    weights = {}
    for i, item in enumerate(r.x):
        weights[predictions_df.columns[i]] = item
    return r.fun, weights


def url_to_bucket_and_prefix(url):
    shards = url.split("/")
    bucket_name = shards[2]
    prefix = '/'.join(shards[3:])
    return bucket_name, prefix


def check_artifact_count(url, expectation):
    bucket_name, prefix = url_to_bucket_and_prefix(url)
    storage_client = storage.Client(project=COMMON['data_stocks_project_name'])
    artifacts_list = list(storage_client.list_blobs(bucket_or_name=bucket_name, prefix=prefix))
    artifacts_list = [item for item in artifacts_list if len(item.name.split(".")) == 2]
    if isinstance(expectation, str):
        return eval(f"{len(artifacts_list)}{expectation}")
    elif isinstance(expectation, int) or isinstance(expectation, float):
        return len(artifacts_list) == expectation
    else:
        raise TypeError(f"Expectation should be either string, integer, or float. Got {type(expectation)}.")


def check_column_not_null(local_filename, expectation):
    df = read_csv(local_filename)
    if any(df.iloc[:, expectation].isna().values.flatten()):
        return False
    return True


def check_column_names(local_filename, expectation):
    col_names = read_csv(local_filename, nrows=1).columns
    for i, name in enumerate(col_names):
        if name != expectation[i]:
            return False
    return True


def check_number_of_columns(local_filename, expectation):
    if len(read_csv(local_filename, nrows=1).columns) != expectation:
        return False
    return True


def check_artifact_structure(url, artifact_type):

    check_dict = {}
    with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'config/checks.yaml'), 'r') as f:
        checks_config = safe_load(f)

    no_artifact_specific_checks = {}
    if artifact_type in checks_config['no_artifact_required'].keys():
        no_artifact_specific_checks = checks_config['no_artifact_required'][artifact_type]
    no_artifact_required_checks = {**checks_config['no_artifact_required']['common'], **no_artifact_specific_checks}

    for check, expectation in no_artifact_required_checks.items():
        if isinstance(expectation, str):
            expectation_arg = f"\'{expectation}\'"
        else:
            expectation_arg = expectation
        check_dict[check] = eval(f"check_{check}(\'{url}\', {expectation_arg})")

    artifact_common_checks = {}
    artifact_specific_checks = {}
    if artifact_type in checks_config['artifact_required'].keys():
        artifact_specific_checks = checks_config['artifact_required'][artifact_type]
    if 'common' in checks_config['artifact_required'].keys():
        artifact_common_checks = checks_config['artifact_required'][artifact_type]
    artifact_required_checks = {**artifact_common_checks, **artifact_specific_checks}

    bucket_name, prefix = url_to_bucket_and_prefix(url)
    storage_client = storage.Client(project=COMMON['data_stocks_project_name'])
    artifacts_list = list(storage_client.list_blobs(bucket_or_name=bucket_name, prefix=prefix))
    artifacts_list = [item for item in artifacts_list if len(item.name.split(".")) == 2]

    with TemporaryDirectory() as tmp:
        for artifact in artifacts_list:
            local_filename = os.path.join(tmp, artifact.name.split("/")[-1])
            artifact.download_to_filename(local_filename)

            for check, expectation in artifact_required_checks.items():
                if isinstance(expectation, str):
                    expectation_arg = f"\'{expectation}\'"
                else:
                    expectation_arg = expectation
                check_dict[check] = eval(f"check_{check}(\'{local_filename}\', {expectation_arg})")

            os.remove(local_filename)

    return all(item is True for item in check_dict.values()), check_dict


def create_artifact_quality_certificate(url, challenge):

    with TemporaryDirectory() as tmp:
        local_filename = os.path.join(tmp, 'quality_certificate.txt')
        with open(local_filename, 'w') as f:
            f.write("")

        storage_client = storage.Client(project=COMMON['website_project_name'])
        bucket_name, prefix = url_to_bucket_and_prefix(url)
        blob = storage_client.bucket(bucket_name).blob(f'{challenge}/quality/quality_certificate.txt')
        blob.upload_from_filename(local_filename)


def create_artifact_issue_report(url, challenge, process_checks, transform_checks):

    d = {'process': {}, 'transform': {}}
    with TemporaryDirectory() as tmp:
        local_filename = os.path.join(tmp, 'quality_issues.json')
        for k, v in process_checks.items():
            if not v:
                d['process'][k] = v
        for k, v in transform_checks.items():
            if not v:
                d['transform'][k] = v
        with open(local_filename, 'w') as f:
            dump(d, f)

        storage_client = storage.Client(project=COMMON['website_project_name'])
        bucket_name, prefix = url_to_bucket_and_prefix(url)
        blob = storage_client.bucket(bucket_name).blob(f'{challenge}/quality_issues/quality_issues.json')
        blob.upload_from_filename(local_filename)


def _get_disk_prep_vm_info(freeze_timestamp, d, user_id, **kwargs):
    try:
        disk_prep_vm_uptime = compute_resource_uptime(d['delete-disk-prep-vm'], d['create-disk-prep-vm'])
        disk_prep_vm_resource_id = COMMON['dim_cloud_resource'][
            kwargs['task_instance'].xcom_pull(task_ids='create-disk-prep-vm', key='machine-type')]
        disk_prep_vm_zone = kwargs['task_instance'].xcom_pull(task_ids='create-disk-prep-vm', key='zone')
        disk_prep_job_id = '#'
        return ['user-disk-prep', user_id, kwargs['run_id'], disk_prep_job_id, freeze_timestamp, disk_prep_vm_resource_id,
                disk_prep_vm_zone, disk_prep_vm_uptime, 'NULL']
    except KeyError:
        return ['user-disk-prep', user_id, kwargs['run_id'], '#', freeze_timestamp, '1', 'no zone', 0., 'NULL']


def _get_bq_execution_info(freeze_timestamp, client, user_id, execution_type=None, **kwargs):
    if execution_type == 'train':
        bq_jobs = kwargs['task_instance'].xcom_pull(task_ids='bq-execution-train', key='jobs')
        key = 'bq-execution-train'
    elif execution_type == 'eval':
        bq_jobs = kwargs['task_instance'].xcom_pull(task_ids='bq-execution-eval', key='jobs')
        key = 'bq-execution-eval'
    elif execution_type == 'inference':
        bq_jobs = kwargs['task_instance'].xcom_pull(task_ids='bq-execution-inference', key='jobs')
        key = 'bq-execution-inference'
    else:
        raise ValueError(f"execution_type must be either 'train', 'eval' or 'inference'. Got {execution_type}.")
    bq_execution_info = []
    if bq_jobs:
        for job_id in bq_jobs:
            jid = job_id.replace('\n', '').replace('\"', '').replace('\'', '')
            job = client.get_job(job_id=jid)
            bq_execution_time = job.ended - job.created
            bq_execution_resource_id = 301
            bq_execution_zone = job.location
            bq_execution_volume = job.total_bytes_billed / 1e9  # volume in GB
            bq_execution_info.append([key, user_id, kwargs['run_id'], jid, freeze_timestamp,
                                      bq_execution_resource_id,
                                      bq_execution_zone, bq_execution_time, bq_execution_volume])
    return bq_execution_info


def _get_data_sync_bq_gcs_info(freeze_timestamp, client, user_id, execution_type=None, **kwargs):
    if execution_type == 'train':
        bq_extraction_jobs = kwargs['task_instance'].xcom_pull(task_ids='sync-train-data-bq-gcs', key='jobs')
        key = 'bq-extraction-train'
    elif execution_type == 'train-user':
        bq_extraction_jobs = kwargs['task_instance'].xcom_pull(task_ids='sync-train-data-user-bq-gcs', key='jobs')
        key = 'bq-extraction-train-user'
    elif execution_type == 'eval':
        bq_extraction_jobs = kwargs['task_instance'].xcom_pull(task_ids='sync-eval-data-bq-gcs', key='jobs')
        key = 'bq-extraction-eval'
    elif execution_type == 'eval-user':
        bq_extraction_jobs = kwargs['task_instance'].xcom_pull(task_ids='sync-eval-data-user-bq-gcs', key='jobs')
        key = 'bq-extraction-eval-user'
    elif execution_type == 'inference':
        bq_extraction_jobs = kwargs['task_instance'].xcom_pull(task_ids='sync-inference-data-bq-gcs', key='jobs')
        key = 'bq-extraction-inference'
    elif execution_type == 'inference-user':
        bq_extraction_jobs = kwargs['task_instance'].xcom_pull(task_ids='sync-inference-data-user-bq-gcs', key='jobs')
        key = 'bq-extraction-inference-user'
    else:
        raise ValueError(f"execution_type must be either 'train', 'eval' or 'eval-user'. Got '{execution_type}'.")
    bq_e_execution_info = []
    if bq_extraction_jobs:
        for job_id, n_bytes in bq_extraction_jobs.items():
            jid = job_id.replace('\n', '').replace('\"', '').replace('\'', '')  # XCom data are posted as string
            job = client.get_job(job_id=jid)
            bq_e_execution_time = job.ended - job.created
            bq_e_execution_resource_id = 301
            bq_e_execution_zone = job.location
            bq_e_execution_volume = n_bytes / 1e9  # volume in GB
            bq_e_execution_info.append([key, user_id, kwargs['run_id'], jid, freeze_timestamp,
                                        bq_e_execution_resource_id,
                                        bq_e_execution_zone, bq_e_execution_time, bq_e_execution_volume])
    return bq_e_execution_info


def _get_data_sync_gcs_disk_info(freeze_timestamp, d, user_id, execution_type=None, **kwargs):
    if execution_type == 'train':
        task_name = 'sync-train-data-gcs-disk'
    elif execution_type == 'eval':
        task_name = 'sync-eval-data-gcs-disk'
    elif execution_type == 'inference':
        task_name = 'sync-inference-data-gcs-disk'
    else:
        raise ValueError(f"execution_type must be either 'train', 'eval' or 'inference'. Got '{execution_type}'.")
    dsync_gcsdisk_uptime = d[task_name]['duration'] or 0
    dsync_gcsdisk_volume = kwargs['task_instance'].xcom_pull(task_ids=task_name, key='data_volume_gb') or 0
    dsync_gcsdisk_resource_id = 201
    dsync_gcsdisk_zone = 'all'
    sync_gcsdisk_job_id = '#'
    return [task_name, user_id, kwargs['run_id'], sync_gcsdisk_job_id, freeze_timestamp, dsync_gcsdisk_resource_id,
            dsync_gcsdisk_zone, dsync_gcsdisk_uptime, dsync_gcsdisk_volume]


def coalesce_datetime(dt, coalesce_to_datetime=datetime.datetime.utcnow()):
    if dt is None:
        helpers_logger.warning(f"Coalesced datetime to {coalesce_to_datetime}")
        return coalesce_to_datetime
    return dt


def compute_resource_uptime(finish_task_info, start_task_info):
    default_timestamp = datetime.datetime.utcnow()
    try:
        uptime = coalesce_datetime(finish_task_info['end_date'], default_timestamp) - coalesce_datetime(start_task_info['end_date'], default_timestamp)
    except TypeError:
        uptime = coalesce_datetime(finish_task_info['end_date'], default_timestamp) - \
                       coalesce_datetime(start_task_info['end_date'], default_timestamp).replace(tzinfo=None)
    return uptime


def _get_user_disk_info(freeze_timestamp, d, user_id, **kwargs):
    udisk_resource_id = COMMON['dim_cloud_resource'][
        kwargs['task_instance'].xcom_pull(task_ids='create-user-disk', key='disk-type') + \
        '-' + \
        str(kwargs['task_instance'].xcom_pull(task_ids='create-user-disk', key='disk-size'))]
    udisk_zone = kwargs['task_instance'].xcom_pull(task_ids='create-user-disk', key='zone')
    udisk_job_id = '#'
    udisk_uptime = compute_resource_uptime(d['delete-user-disk'], d['create-user-disk'])
    return ['user-disk', user_id, kwargs['run_id'], udisk_job_id, freeze_timestamp, udisk_resource_id, udisk_zone,
            udisk_uptime, 'NULL']


def _get_sync_repo_info(freeze_timestamp, d, user_id, **kwargs):
    dsync_repo_uptime = d['sync-repo']['duration'] or 0
    dsync_repo_volume = kwargs['task_instance'].xcom_pull(task_ids='sync-repo', key='data_volume_gb') or 0
    dsync_repo_resource_id = 201
    dsync_repo_zone = 'all'
    dsync_repo_job_id = '#'
    return ['sync-repo', user_id, kwargs['run_id'], dsync_repo_job_id, freeze_timestamp, dsync_repo_resource_id,
            dsync_repo_zone, dsync_repo_uptime, dsync_repo_volume]


def _get_sync_code_info(freeze_timestamp, d, user_id, **kwargs):
    dsync_code_uptime = d['sync-code']['duration'] or 0
    dsync_code_volume = kwargs['task_instance'].xcom_pull(task_ids='sync-code', key='data_volume_gb') or 0
    dsync_code_resource_id = 201
    dsync_code_zone = 'all'
    dsync_code_job_id = '#'
    return ['sync-code', user_id, kwargs['run_id'], dsync_code_job_id, freeze_timestamp, dsync_code_resource_id,
            dsync_code_zone, dsync_code_uptime, dsync_code_volume]


def _get_sync_output_info(freeze_timestamp, d, user_id, **kwargs):
    dsync_output_uptime = d['sync-output']['duration'] or 0
    dsync_output_volume = kwargs['task_instance'].xcom_pull(task_ids='sync-output', key='data_volume_gb') or 0
    dsync_output_resource_id = 201
    dsync_output_zone = 'all'
    dsync_output_job_id = '#'
    return ['sync-output', user_id, kwargs['run_id'], dsync_output_job_id, freeze_timestamp, dsync_output_resource_id,
            dsync_output_zone, dsync_output_uptime, dsync_output_volume]


def _get_vault_vm_info(freeze_timestamp, d, user_id, **kwargs):
    try:
        vault_vm_uptime = compute_resource_uptime(d['delete-vault-vm'], d['create-vault-vm'])
        vault_vm_resource_id = COMMON['dim_cloud_resource'][
            kwargs['task_instance'].xcom_pull(task_ids='create-vault-vm', key='machine-type')]
        vault_vm_zone = kwargs['task_instance'].xcom_pull(task_ids='create-vault-vm', key='zone')
        vault_vm_job_id = '#'
        return ['vault-compute', user_id, kwargs['run_id'], vault_vm_job_id, freeze_timestamp, vault_vm_resource_id,
                vault_vm_zone, vault_vm_uptime, 'NULL']
    except KeyError:
        return ['vault-compute', user_id, kwargs['run_id'], '#', freeze_timestamp, '1', 'no zone', 0., 'NULL']


def _get_sync_logs_info(freeze_timestamp, d, user_id, **kwargs):
    dsync_logs_uptime = d['sync-logs']['duration'] or 0
    dsync_logs_volume = kwargs['task_instance'].xcom_pull(task_ids='sync-logs', key='data_volume_gb') or 0
    dsync_logs_resource_id = 201
    dsync_logs_zone = 'all'
    dsync_logs_job_id = '#'
    return ['sync-logs', user_id, kwargs['run_id'], dsync_logs_job_id, freeze_timestamp, dsync_logs_resource_id,
            dsync_logs_zone, dsync_logs_uptime, dsync_logs_volume]


def _get_data_extraction_vm_info(freeze_timestamp, d, user_id, **kwargs):
    try:
        data_extraction_vm_uptime = compute_resource_uptime(d['delete-extraction-vm'], d['create-data-extraction-vm'])
        data_extraction_vm_resource_id = COMMON['dim_cloud_resource'][
            kwargs['task_instance'].xcom_pull(task_ids='create-data-extraction-vm', key='machine-type')]
        data_extraction_vm_zone = kwargs['task_instance'].xcom_pull(task_ids='create-data-extraction-vm', key='zone')
        data_extraction_vm_job_id = '#'
        return ['extraction-compute', user_id, kwargs['run_id'], data_extraction_vm_job_id, freeze_timestamp,
                data_extraction_vm_resource_id, data_extraction_vm_zone, data_extraction_vm_uptime, 'NULL']
    except KeyError:
        return ['extraction-compute', user_id, kwargs['run_id'], '#', freeze_timestamp, '1', 'no zone', 0., 'NULL']


def get_usage_information_common(d, user_id, freeze_timestamp, **kwargs):
    # OK = method works for both 'user_job' and 'inference_job', which entails task names are the same

    # USER DISK
    udisk_info = _get_user_disk_info(freeze_timestamp, d, user_id, **kwargs)  # OK

    # VM(s)
    disk_prep_vm_info = _get_disk_prep_vm_info(freeze_timestamp, d, user_id, **kwargs)  # OK
    vault_vm_info = _get_vault_vm_info(freeze_timestamp, d, user_id, **kwargs)  # OK
    data_extraction_vm_info = _get_data_extraction_vm_info(freeze_timestamp, d, user_id, **kwargs)  # OK

    # DATA SYNC
    dsync_repo_info = _get_sync_repo_info(freeze_timestamp, d, user_id, **kwargs)  # OK
    dsync_code_info = _get_sync_code_info(freeze_timestamp, d, user_id, **kwargs)  # OK
    dsync_logs_info = _get_sync_logs_info(freeze_timestamp, d, user_id, **kwargs)  # OK
    dsync_output_info = _get_sync_output_info(freeze_timestamp, d, user_id, **kwargs)  # OK

    return [udisk_info, disk_prep_vm_info, dsync_repo_info, dsync_code_info,
            dsync_logs_info, dsync_output_info, vault_vm_info, data_extraction_vm_info]


def get_orchestration_service_account(environment):
    if environment == 'DEV':
        return 'airflow-dev-sa'
    elif environment is None:  # PROD
        return 'airflow-prod-sa'
    else:
        raise ValueError(f"Environment must be in (DEV, PROD). Got {environment}")


def get_usage_information_inference_job(d, user_id, **kwargs):
    freeze_timestamp = datetime.datetime.now()
    client = bigquery.Client(project=COMMON['data_stocks_project_name'],
                             location='EU')  # job_ids are project:location.job_id. Risk of not finding jobs without explicit location!
    common_info = get_usage_information_common(d, user_id, freeze_timestamp, **kwargs)

    # Inference job specifics
    # BQ EXECUTION
    bq_execution_inference_info = _get_bq_execution_info(freeze_timestamp, client, user_id, 'inference', **kwargs)

    # BQ DATA SYNC (from BQ to GCS)
    bq_e_execution_inference_info = _get_data_sync_bq_gcs_info(freeze_timestamp, client, user_id, 'inference', **kwargs)
    bq_e_execution_inference_user_info = _get_data_sync_bq_gcs_info(freeze_timestamp, client, user_id, 'inference-user',
                                                                    **kwargs)

    # BQ DATA SYNC (from GCS to Vm disk)
    dsync_inference_gcsdisk_info = _get_data_sync_gcs_disk_info(freeze_timestamp, d, user_id, 'inference', **kwargs)

    # STORE ALL INFO
    info_list = common_info + [dsync_inference_gcsdisk_info] + bq_execution_inference_info + \
                bq_execution_inference_info + \
                bq_e_execution_inference_info + bq_e_execution_inference_user_info
    return info_list


def get_usage_information_user_job(d, user_id, **kwargs):
    freeze_timestamp = datetime.datetime.now()
    client = bigquery.Client(project=COMMON['data_stocks_project_name'],
                             location='EU')  # job_ids are project:location.job_id. Risk of not finding jobs without explicit location!
    common_info = get_usage_information_common(d, user_id, freeze_timestamp, **kwargs)

    # User job specifics
    # BQ EXECUTION
    bq_execution_train_info = _get_bq_execution_info(freeze_timestamp, client, user_id, 'train', **kwargs)
    bq_execution_eval_info = _get_bq_execution_info(freeze_timestamp, client, user_id, 'eval', **kwargs)

    # BQ DATA SYNC (from BQ to GCS)
    bq_e_execution_train_info = _get_data_sync_bq_gcs_info(freeze_timestamp, client, user_id, 'train', **kwargs)
    bq_e_execution_train_user_info = _get_data_sync_bq_gcs_info(freeze_timestamp, client, user_id, 'train-user',
                                                                **kwargs)
    bq_e_execution_eval_info = _get_data_sync_bq_gcs_info(freeze_timestamp, client, user_id, 'eval', **kwargs)
    bq_e_execution_eval_user_info = _get_data_sync_bq_gcs_info(freeze_timestamp, client, user_id, 'eval-user', **kwargs)

    # BQ DATA SYNC (from GCS to Vm disk)
    dsync_train_gcsdisk_info = _get_data_sync_gcs_disk_info(freeze_timestamp, d, user_id, 'train', **kwargs)
    dsync_eval_gcsdisk_info = _get_data_sync_gcs_disk_info(freeze_timestamp, d, user_id, 'eval', **kwargs)

    # STORE ALL INFO
    info_list = common_info + [dsync_train_gcsdisk_info, dsync_eval_gcsdisk_info] + bq_execution_train_info + \
                bq_execution_eval_info + bq_e_execution_train_info + bq_e_execution_train_user_info + \
                bq_e_execution_eval_info + bq_e_execution_eval_user_info
    return info_list


def _bq_data_sync(project, dataset, relevant_tables, data_gcs_path, enable_sharding=False):
    # Transfer from BQ to GCS
    client = bigquery.Client(project=project)
    if not relevant_tables:
        relevant_tables = list(client.list_tables(dataset=dataset))
    extract_jobs = {}
    job_list = []
    job_config = bigquery.job.ExtractJobConfig()
    job_config.compression = bigquery.Compression.GZIP
    for t in relevant_tables:
        table = client.get_table(t)
        table_name = table.table_id.split(".")[-1]
        table_destination_name = f'{table_name}.csv'
        if enable_sharding:
            table_destination_name = f'{table_name}___*.csv'
        extract_job = client.extract_table(source=table,
                                           destination_uris=os.path.join(data_gcs_path, table_destination_name + '.gz'),
                                           job_config=job_config)
        extract_jobs[extract_job.job_id] = table.num_bytes
        job_list.append(extract_job)
    for job in job_list:
        job.result()
    return extract_jobs


def write_dag_run_request(dag=None, run_id=None, conf=None, project=None, bucket_name=None):
    client = storage.Client(project=project)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f'user_requests/{dag}/{run_id}')
    blob.upload_from_string(dumps(conf))


def create_disk(project_id, zone, name, size, type):
    disk_client = compute_v1.DisksClient()
    operation_client = compute_v1.ZoneOperationsClient()

    disk_resource = compute_v1.types.compute.Disk()
    disk_resource.name = name
    disk_resource.size_gb = size
    disk_resource.type_ = type

    request = compute_v1.types.compute.InsertDiskRequest()
    request.project = project_id
    request.disk_resource = disk_resource
    request.zone = zone

    # Wait for the create operation to complete.
    print(f"Creating the {name} disk in {zone}...")
    operation = disk_client.insert_unary(request=request)
    while operation.status != compute_v1.Operation.Status.DONE:
        operation = operation_client.wait(
            operation=operation.name, zone=zone, project=project_id
        )
    if operation.error:
        print("Error during creation:", operation.error, file=sys.stderr)
        raise ChildProcessError(operation.error)
    if operation.warnings:
        print("Warning during creation:", operation.warnings, file=sys.stderr)
    print(f"Disk {name} created.")


def create_instance(project_id, zone, instance_name, machine_type,
                    source_image="projects/debian-cloud/global/images/family/debian-10",
                    network_name="global/networks/default", additional_disks=[], add_external_ip=False,
                    service_account=None, startup_script=None) -> compute_v1.Instance:
    """
        Send an instance creation request to the Compute Engine API and wait for it to complete.

        Args:
            project_id: project ID or project number of the Cloud project you want to use.
            zone: name of the zone you want to use. For example: “us-west3-b”
            instance_name: name of the new virtual machine.
            machine_type: machine type of the VM being created. This value uses the
                following format: "zones/{zone}/machineTypes/{type_name}".
                For example: "zones/europe-west3-c/machineTypes/f1-micro"
            source_image: path to the operating system image to mount on your boot
                disk. This can be one of the public images
                (like "projects/debian-cloud/global/images/family/debian-10")
                or a private image you have access to.
            network_name: name of the network you want the new instance to use.
                For example: "global/networks/default" represents the `default`
                network interface, which is created automatically for each project.
        Returns:
            Instance object.
        """
    instance_client = compute_v1.InstancesClient()
    operation_client = compute_v1.ZoneOperationsClient()

    # Describe the size and source image of the boot disk to attach to the instance.
    disk = compute_v1.AttachedDisk()
    initialize_params = compute_v1.AttachedDiskInitializeParams()
    initialize_params.source_image = (
        source_image  # "projects/debian-cloud/global/images/family/debian-10"
    )
    initialize_params.disk_size_gb = 10
    disk.initialize_params = initialize_params
    disk.auto_delete = True
    disk.boot = True
    disk.type_ = "PERSISTENT"

    other_disks = []
    for item in additional_disks:
        tmp_disk = compute_v1.AttachedDisk()
        tmp_disk.device_name = item['device_name']
        tmp_disk.auto_delete = False
        tmp_disk.boot = False
        tmp_disk.mode = item['mode']
        tmp_disk.source = item['url']
        other_disks.append(tmp_disk)

    # Use the network interface provided in the network_name argument.
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = network_name
    if add_external_ip:  # get an external IP for the VM
        access_config = compute_v1.types.AccessConfig()
        access_config.name = 'External NAT'
        network_interface.access_configs = [access_config]

    # Add service account
    if service_account:
        instance_sa = compute_v1.types.ServiceAccount()
        instance_sa.email = service_account['email']
        instance_sa.scopes = service_account['scopes']

    # Add startup script
    if startup_script:
        instance_metadata = compute_v1.types.Metadata()
        instance_start_script = compute_v1.types.Items()
        instance_start_script.key = 'startup-script'
        instance_start_script.value = startup_script
        instance_metadata.items = [instance_start_script]

    # Collect information into the Instance object.
    instance = compute_v1.Instance()
    instance.name = instance_name
    instance.disks = [disk] + other_disks
    if re.match(r"^zones/[a-z\d\-]+/machineTypes/[a-z\d\-]+$", machine_type):
        instance.machine_type = machine_type
    else:
        instance.machine_type = f"zones/{zone}/machineTypes/{machine_type}"
    instance.network_interfaces = [network_interface]
    if service_account:
        instance.service_accounts = [instance_sa]
    if startup_script:
        instance.metadata = instance_metadata

    # Prepare the request to insert an instance.
    request = compute_v1.InsertInstanceRequest()
    request.zone = zone
    request.project = project_id
    request.instance_resource = instance

    # Wait for the create operation to complete.
    print(f"Creating the {instance_name} instance in {zone}...")
    operation = instance_client.insert_unary(request=request)
    while operation.status != compute_v1.Operation.Status.DONE:
        operation = operation_client.wait(
            operation=operation.name, zone=zone, project=project_id
        )
    if operation.error:
        print("Error during creation:", operation.error, file=sys.stderr)
    if operation.warnings:
        print("Warning during creation:", operation.warnings, file=sys.stderr)

    return operation


def send_email(api_key, from_email, to_emails, subject, html_content):
    message = Mail(from_email=from_email,
                   to_emails=to_emails,
                   subject=subject,
                   html_content=html_content)

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)


def reminder_via_email(config, d, challenge, until):
    for email, values in d.items():
        send_email(api_key=config['api_key'],
                   from_email=config['join_round_reminder']['from_email'],
                   to_emails=email,
                   subject=config['join_round_reminder']['subject'],
                   html_content=Template(config['join_round_reminder']['html_content'])
                   .render({'username': values['username'], 'challenge': challenge, 'until': until}))


def heartbeat_via_email(config, d):
    for email, values in d.items():
        send_email(api_key=config['api_key'],
                   from_email=config['heartbeat']['from_email'],
                   to_emails=email,
                   subject=config['heartbeat']['subject'],
                   html_content=Template(config['heartbeat']['html_content']).render())

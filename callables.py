"""
Airflow python callables. These functions handle all I/O and XCom logic. They rely on functions from
helpers.py for any other logic implementation.
"""

import os
import time
import datetime
import json
import helpers
import string
from random import choices
from logging import getLogger
from pandas import read_csv, concat, StringDtype
from yaml import safe_load
from zipfile import ZipFile
import google.api_core.exceptions
import subprocess
from pathlib import Path
from importlib import import_module
from tempfile import TemporaryDirectory
import google.cloud.compute_v1 as compute_v1
from google.cloud import bigquery, storage
from jinja2 import Template
from globals import CHALLENGES

PATH = os.path.abspath(os.path.dirname(__file__))
SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql')
callables_logger = getLogger('Callables_Logger')

with open(os.path.join(Path(__file__).parent.resolve(), 'config/common.yaml'), 'r') as f:
    COMMON = safe_load(f)


def publish_run_parameters(run_dict, **kwargs):
    for k, v in run_dict.items():
        kwargs['task_instance'].xcom_push(key=k, value=v)


def score_metamodel(inference_dir, metamodel_dir, **kwargs):
    with TemporaryDirectory() as tmp_dir:
        cmd_inference = f"gsutil rsync -r {inference_dir} {tmp_dir}"
        cmd_metamodel = f"gsutil rsync -r {metamodel_dir} {tmp_dir}"
        subprocess.run(cmd_inference, shell=True)
        subprocess.run(cmd_metamodel, shell=True)

        # Load metamodel
        with open(os.path.join(tmp_dir, 'metamodel.json'), 'r') as f:
            metamodel = json.load(f)

        dfs = []
        for k, v in metamodel['weights'].items():
            tmp_df = read_csv(os.path.join(tmp_dir, k, 'predictions.csv'))
            tmp_df['pred'] *= v
            tmp_df.set_index(['OBS_DATE', 'Ticker'], drop=True, inplace=True)
            dfs.append(tmp_df)
        metamodel_df = concat(dfs, axis=1).sum(axis=1).reset_index()
        metamodel_df.rename(columns={0: 'pred'}, inplace=True)

        metamodel_uri = os.path.join(tmp_dir, 'metamodel.csv')
        metamodel_df.to_csv(path_or_buf=metamodel_uri, index=False)

        cmd_export = f'gsutil cp {metamodel_uri} {metamodel_dir}'
        subprocess.run(cmd_export, shell=True)


def trigger_inference_jobs(obs_date, artifact_bucket, artifact_prefix,
                           active_prefix, active_user_destination_uri, environment, challenge_dict, **kwargs):
    # List available artifacts
    client = storage.Client()
    eligible_artifacts = list(client.list_blobs(bucket_or_name=artifact_bucket, prefix=artifact_prefix))
    eligible_users = list(set([blob.name.split("/")[-2] for blob in eligible_artifacts]))

    # Get user buckets
    user_buckets_and_ids = helpers.get_user_bucket(eligible_users, return_users=True)

    # Trigger only inference jobs with the 'active' participation flag
    active_inference = []
    inactive_inference = []
    for bucket, user in user_buckets_and_ids:
        current_is_active = list(client.list_blobs(bucket_or_name=bucket, prefix=active_prefix))
        if current_is_active or environment == 'DEV':
            inference_conf = {"user_id": user,
                              "resource_suffix": f"inference-{user.lower()}",
                              "project": challenge_dict['project_name'],
                              "orchestration_sa": helpers.get_orchestration_service_account(environment),
                              "zone": helpers.choose_compute_zone(),
                              "challenge": challenge_dict['name'],
                              "repo_gcs_path": f"gs://{COMMON['pypi_repo_bucket_name']}/",
                              "code_gcs_path": f"gs://{bucket}/{challenge_dict['name']}/code/",
                              "artifacts_gcs_path": f"gs://{challenge_dict['bucket']}/artifacts/{user}/",
                              "data_gcs_path": f"gs://{challenge_dict['bucket']}/tmp_inference/{obs_date}/{user}/",
                              "logs_gcs_path": f"gs://{challenge_dict['bucket']}/inference_logs/{obs_date}/{user}/",
                              "user_dataset": helpers.get_user_dataset(user),
                              "output_gcs_path": f"gs://{challenge_dict['bucket']}/inference/{obs_date}/predictions/{user}/",
                              "dag_retries": 0
                              }
            json_conf = json.dumps(inference_conf)
            run_id = f"{user}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            cmd = f"airflow dags trigger --conf \'{json_conf}\' " \
                  f"--run-id {run_id} {challenge_dict['name']}_inference_job"
            trigger_dag_status = subprocess.run(cmd, shell=True)
            active_inference.append(user)
            continue
        inactive_inference.append(user)

    with TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'active.txt'), 'w') as f:
            for item in active_inference:
                f.write(item + '\n')

        cmd = f"gsutil rsync -r {tmp} {active_user_destination_uri}"
        subprocess.run(cmd, shell=True)

    kwargs['task_instance'].xcom_push(key='active_inference', value=active_inference)
    kwargs['task_instance'].xcom_push(key='inactive_inference', value=inactive_inference)


def activate_bot_submissions(bot_names=None, challenge=None):
    with open(os.path.join(PATH, 'bots/submissions_config.yaml'), 'r') as f:
        config = safe_load(f)

    active_bot_names = []
    for bot_name in bot_names:
        if config[bot_name]['active']:
            active_bot_names.append(bot_name)

    bot_names_str = ''.join([f"\'{config[bot_name]['email']}\'," for bot_name in active_bot_names])[0:-1]
    user_buckets = [item[0] for item in helpers.run_query(
        "select bucket_id from user_registry where user_email IN (" + bot_names_str + ") and deleted_on IS NULL")]

    client = storage.Client()
    for b in user_buckets:
        bucket = client.get_bucket(b)
        blob = bucket.blob(f"{challenge}/active/active.txt")
        with blob.open(mode='w') as mf:
            mf.write("")


def bot_trigger(bot_name=None, challenge=None, **kwargs):
    with open(os.path.join(PATH, 'bots/submissions_config.yaml'), 'r') as f:
        config = safe_load(f)

    if config[bot_name]['active'][challenge]:

        user_info = helpers.run_query(
            "select user_id, bucket_id, dataset_id from user_registry where user_email=\'" + config[bot_name][
                'email'] + "\'" + " and deleted_on is null")
        user = user_info[0][0]
        user_bucket = user_info[0][1]
        user_dataset = user_info[0][2]

        conf = {
            "user_id": user,
            "resource_suffix": f"{user.lower()}-{''.join(choices(string.ascii_lowercase + string.digits, k=5))}",
            "project": CHALLENGES[challenge]['project_name'],
            "zone": helpers.choose_compute_zone(),
            "repo_gcs_path": f"gs://{COMMON['pypi_repo_bucket_name']}/",
            "code_gcs_path": f"gs://{user_bucket}/{challenge}/code/",
            "data_gcs_path": f"gs://{CHALLENGES[challenge]['bucket']}/tmp/{user}/",
            "logs_gcs_path": f"gs://{user_bucket}/{challenge}/logs/",
            "user_dataset": user_dataset,
            "artifacts_gcs_path": f"gs://{CHALLENGES[challenge]['bucket']}/artifacts/{user}/",
            "evaluation_gcs_path": f"gs://{CHALLENGES[challenge]['bucket']}/evaluation/{user}/",
            "dag_retries": 0,
            "challenge": challenge
        }

        run_id = user + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        helpers.write_dag_run_request(dag=f'{challenge}_user_job', run_id=run_id,
                                      conf=conf, project=CHALLENGES[challenge]['project_name'],
                                      bucket_name=CHALLENGES[challenge]['bucket'])

    else:
        callables_logger.info(f"{bot_name} is not active for challenge {challenge}. Skipping trigger...")


def submit_bot_code(bot_name=None, challenge=None, **kwargs):
    with open(os.path.join(PATH, 'bots/submissions_config.yaml'), 'r') as f:
        config = safe_load(f)
    callables_logger.info(f"Bot configuration file is {config}")

    if config[bot_name]['active'][challenge]:
        query_statement = 'select bucket_id from user_registry where user_email = \'' + config[bot_name]['email'] + \
                          '\'' + ' and deleted_on is null'
        results = helpers.run_query(query_statement)

        with TemporaryDirectory() as tmpdir:
            zip_filename = os.path.join(tmpdir, f"{bot_name}.zip")
            with ZipFile(zip_filename, 'w') as f:
                target_directory = os.path.join(PATH, f'bots/{bot_name}')
                callables_logger.info(f"Zip file will be created from directory: {target_directory}")
                for folderName, subfolders, filenames in os.walk(target_directory):
                    callables_logger.info(
                        f"Walking. Folder name: {folderName}, subfolders: {subfolders}, filenames: {filenames}")
                    for filename in filenames:
                        filepath = os.path.join(folderName, filename)
                        if filename == 'requirements.txt':
                            f.write(filepath, os.path.basename(filepath))
                        else:
                            f.write(filepath, os.path.join(folderName.split("/")[-1], os.path.basename(filepath)))

            cmd = f"gsutil cp {zip_filename} gs://{results[0][0]}/{challenge}/code/{zip_filename.split('/')[-1]}"
            subprocess.run(cmd, shell=True)
    else:
        callables_logger.info(f"{bot_name} is not active. Skipping submission...")


def update_transaction_w_prize(ref_date=None, problem_id=None, **kwargs):
    with open(os.path.join(PATH, 'sql/get_prize_assignment.sql'), 'r') as f:
        query_statement = Template(''.join(f.readlines())).render(reference_date=ref_date,
                                                                  problem_identifier=problem_id)
    results = helpers.run_query(query_statement)

    insert_statement = 'insert into public.user_transactions values '
    for row in results:
        insert_statement += helpers.list2dbstr([row[0], f'prize-{ref_date}', 'prize', 'USD', 'NULL',
                                                datetime.datetime.now(), True, 'prize', row[1]]) + ', '
    insert_statement = insert_statement[0: -2]
    helpers.run_insert_statement(insert_statement)


def update_leaderboard():
    insert_statement = 'call user_leaderboard()'
    helpers.run_insert_statement(insert_statement)


def assign_prize_pool(ref_date=None, problem_id=None, amount=None, **kwargs):
    insert_sql = f"insert into public.prize_pool values (\'{ref_date}\', \'{problem_id}\', \'{amount}\')"
    helpers.run_insert_statement(insert_sql)


def assign_prizes(ref_date=None, problem_id=None, source_uri=None, **kwargs):
    # Fetch metamodel built on true targets
    with TemporaryDirectory() as tmp:
        cmd = f"gsutil rsync -r {source_uri} {tmp}"
        subprocess.run(cmd, shell=True)

        with open(os.path.join(tmp, 'metamodel.json'), 'r') as f:
            metamodel = json.load(f)

    # Compute insert string
    insert_prefix = "insert into public.prize_assignment values "
    values = ''
    for k, v in metamodel['weights'].items():
        values += f"(\'{ref_date}\', \'{problem_id}\', \'{k}\', {v}),"
    insert_sql = insert_prefix + values[0:-1]

    # Insert to DB
    helpers.run_insert_statement(insert_sql)


def build_metamodel(sources=None, destination_uri=None, challenge_dict=None, **kwargs):
    """
    Builds metamodel as a mixture of individual (active) user predictions.
    :param sources: (dict). Dictionary containing reference to files ('predictions', 'active_users')
    :param destination_uri: (str)
    :param kwargs:
    :return:
    """

    with TemporaryDirectory() as metamodel_dir:

        # Fetch user predictions from buckets
        sync_cmd = f"gsutil -m rsync -r {sources['predictions_uri']} {metamodel_dir}"
        output = subprocess.run(sync_cmd, shell=True, check=True, capture_output=True)
        if output.returncode != 0:
            print(output.returncode)
            print(output.stderr)
            raise Exception

        # Fetch active users
        sync_cmd = f"gsutil -m rsync -r {sources['active_users_uri']} {metamodel_dir}"
        output = subprocess.run(sync_cmd, shell=True, check=True, capture_output=True)
        if output.returncode != 0:
            print(output.returncode)
            print(output.stderr)
            raise Exception
        with open(os.path.join(metamodel_dir, 'active.txt'), 'r') as f:
            active_users = [item.replace('\n', '') for item in f.readlines()]

        prediction_dict = {}
        for (dirpath, dirnames, _) in os.walk(metamodel_dir):
            for dirname in dirnames:
                for (_, _, filenames) in os.walk(os.path.join(dirpath, dirname)):
                    if dirname in active_users:
                        for file in filenames:  # !!! Unintended behavior if more than one file is found
                            prediction_dict[dirname] = os.path.join(dirpath, dirname, file)

        predictions_df = None
        for key, item in prediction_dict.items():
            tmp_df = read_csv(filepath_or_buffer=item)
            tmp_df.rename(columns={'pred': key}, inplace=True)
            tmp_df = tmp_df[~tmp_df['OBS_DATE'].isna()]  # TODO: remove. Useful only for prize backfill.
            if predictions_df is not None:
                predictions_df = predictions_df.merge(tmp_df, how='outer', on=['OBS_DATE', 'Ticker'])
                continue
            predictions_df = tmp_df

    # Fetch targets
    start_obs_date = predictions_df['OBS_DATE'].min()
    end_obs_date = predictions_df['OBS_DATE'].max()
    with open(os.path.join(PATH, f"challenges/{challenge_dict['name']}/sql/get_target_at_date.sql"), 'r') as f:
        query_template = Template(''.join(f.readlines()))
    query_statement = query_template.render(project=challenge_dict['project_name'],
                                            start_obs_date=start_obs_date, end_obs_date=end_obs_date)
    bq_client = bigquery.Client()
    target_df = bq_client.query(query_statement).to_dataframe()
    target_df['OBS_DATE'] = target_df['OBS_DATE'].astype(StringDtype())  # necessary otherwise merge w/ target fails
    if target_df.empty:
        raise ValueError(f"Target DataFrame is empty for observation dates {start_obs_date} {end_obs_date}.")

    # Run optimization / build metamodel
    merged_dataframe = target_df.merge(predictions_df, how='left', on=['OBS_DATE', 'Ticker'])
    prediction_columns = [col for col in merged_dataframe.columns if
                          col not in ('OBS_DATE', 'Ticker', 'TARGET_VARIABLE')]
    # Should there be NULL predictions, they are filled with 0.5 (i.e. non-informative value)
    metamodel_performance, metamodel_weights = helpers.build_metamodel(merged_dataframe[prediction_columns].fillna(0.5),
                                                                       merged_dataframe[
                                                                           'TARGET_VARIABLE'].to_numpy().astype('int'))
    metamodel = {'performance': metamodel_performance, 'weights': metamodel_weights}

    # Export metamodel weights
    with TemporaryDirectory() as metamodel_dir:
        with open(os.path.join(metamodel_dir, 'metamodel.json'), 'w') as f:
            json.dump(metamodel, f)
        export_cmd = f'gsutil -m rsync -r {metamodel_dir} {destination_uri}'
        output = subprocess.run(export_cmd, shell=True, check=True, capture_output=True)
        if output.returncode != 0:
            print(output.returncode)
            print(output.stderr)
            raise Exception


def update_user_transactions(**kwargs):
    if kwargs['dag_run'].execution_date < datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(hours=1):
        return  # skip execution if too far away in the past (useful to avoid DB congestion)

    # Send to DB
    insert_statement = "call update_user_transactions()"
    helpers.run_insert_statement(insert_statement)


def update_user_credits_and_wallet(**kwargs):
    # Send to DB
    insert_statement = "call user_current_credits_and_wallet()"
    helpers.run_insert_statement(insert_statement)


def publish_job_run(user_id, challenge=None, **kwargs):
    user_bucket = helpers.get_user_bucket(user_id=user_id)
    storage_client = storage.Client(project=COMMON['website_project_name'])
    bucket = storage_client.get_bucket(user_bucket)
    blob = bucket.blob(f"{challenge}/running_job/running.txt")
    with blob.open(mode='w') as mf:
        mf.write("")


def delete_publish_job_run(user_id, challenge=None, **kwargs):
    user_bucket = helpers.get_user_bucket(user_id=user_id)
    storage_client = storage.Client(project=COMMON['website_project_name'])
    blobs = list(storage_client.list_blobs(bucket_or_name=user_bucket, prefix=f"{challenge}/running_job"))
    for blob in blobs:
        blob.delete()


def reset_user_sub_status(active_users_uri=None, challenge=None, **kwargs):
    with TemporaryDirectory() as tmp:

        cmd = f'gsutil -m rsync -r {active_users_uri} {tmp}'
        output = subprocess.run(cmd, shell=True, check=True, capture_output=True)
        if output.returncode != 0:
            print(output.returncode)
            print(output.stderr)
            return output.stderr

        with open(os.path.join(tmp, 'active.txt'), 'r') as f:
            users = [item.rstrip('\n') for item in f.readlines()]

        bucket_list = helpers.get_user_bucket(users)
        storage_client = storage.Client(project=COMMON['website_project_name'])
        for bucket in bucket_list:
            blob_list = list(storage_client.list_blobs(bucket_or_name=bucket[0], prefix=f"{challenge}/active"))
            for blob in blob_list:
                blob.delete()


def get_bq_sandbox_usage(**kwargs):
    # Meant to run daily
    client = bigquery.Client()

    # print(kwargs['dag_run'].execution_date)
    min_creation_time = kwargs['dag_run'].execution_date
    max_creation_time = kwargs['dag_run'].execution_date + datetime.timedelta(days=1)
    bq_jobs = list(client.list_jobs(project=COMMON['backend_project_name'], all_users=True, state_filter='done',
                                    min_creation_time=min_creation_time,
                                    max_creation_time=max_creation_time))
    print(bq_jobs)
    info_list = []
    for job in bq_jobs:
        if job.user_email in COMMON['backend_user_emails']:
            continue  # don't bill backend users
        if job.job_type == 'copy' or job.total_bytes_billed is None:
            total_bytes_billed = 0
        else:
            total_bytes_billed = job.total_bytes_billed
        info_list.append([job.job_id, job.user_email, job.location, 301, job.created, job.ended, total_bytes_billed])
        if job.destination is None:
            continue
        if not (job.destination.table_id.startswith('anon') and len(job.destination.table_id) == 44):
            try:
                destination_table = client.get_table(job.destination)
            except google.api_core.exceptions.NotFound:
                continue  # probably means the user was deleted, unable to bill latest operations
            info_list.append([job.job_id, job.user_email, destination_table.location, 302, destination_table.created,
                              destination_table.expires, destination_table.num_bytes])
    info_insert_string = ""
    for item in info_list:
        info_insert_string += helpers.list2dbstr(item) + ", "
    info_insert_string = info_insert_string[0:-2]

    if info_list:  # connect to DB only if there are information to send
        insert_statement = "insert into public.bq_sandbox_usage values " + info_insert_string
        helpers.run_insert_statement(insert_statement)


def get_usage_information(mode, task_instance_list, user_id, **kwargs):
    # Make task_instance_list a dictionary
    d = {}
    for task in task_instance_list:
        d[task.task_id] = {}
        d[task.task_id]['task_instance'] = task
        d[task.task_id]['start_date'] = task.start_date
        d[task.task_id]['end_date'] = task.end_date
        d[task.task_id]['duration'] = task.duration
        d[task.task_id]['dag_id'] = task.dag_id

    # Fetch information from tasks and XCom
    if mode == 'user':
        info = helpers.get_usage_information_user_job(d, user_id, **kwargs)
    elif mode == 'inference':
        info = helpers.get_usage_information_inference_job(d, user_id, **kwargs)
    else:
        raise ValueError(f"Mode can be one of: 'user', 'inference'. Got {mode}.")

    # Store information in DB
    info_insert_string = ''
    for item in info:
        info_insert_string += helpers.list2dbstr(item) + ", "
    info_insert_string = info_insert_string[0:-2]
    print(info_insert_string)

    insert_statement = "insert into public.cloud_usage values " + info_insert_string
    helpers.run_insert_statement(insert_statement)


def compute_and_send_metrics(challenge, dataset, user_id, **kwargs):

    client = bigquery.Client(project=CHALLENGES[challenge]['project_name'])
    query_statement = f"""SELECT s.target_variable, p.pred as prediction
    FROM `{CHALLENGES[challenge]['project_name']}.evaluation_layer.t_target` s
    JOIN `{CHALLENGES[challenge]['project_name']}.{dataset}.eval_predictions` p
    ON s.obs_date = p.date
    AND s.ticker = p.ticker"""
    df = client.query(query_statement).to_dataframe()

    challenge_metrics_module = import_module(f"challenges.{challenge}.source.{challenge}")
    fn_callable = getattr(challenge_metrics_module, 'official_evaluation_metric')
    metrics = fn_callable(df['target_variable'], df['prediction'])

    data_gcs_path = f"gs://{helpers.get_user_bucket(user_id)}/{CHALLENGES[challenge]['name']}/model_evaluations/eval_metrics.json"

    with TemporaryDirectory() as tmpdir:
        json_file_path = os.path.join(tmpdir, 'eval_metrics.json')
        with open(json_file_path, 'w') as f:
            json.dump(metrics, f)

        cmd = f'gsutil cp {json_file_path} {data_gcs_path}'
        output = subprocess.run(cmd, shell=True, check=True, capture_output=True)
        if output.returncode != 0:
            print(output.returncode)
            print(output.stderr)
            return output.stderr


def bq_execution(cmd, **kwargs):
    output = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    if output.returncode != 0:
        print(output.returncode)
        print(output.stderr)
        return output.stderr
    job_list = list(output.stdout.decode('utf-8').replace(' ', '').replace('[', '').replace(']', '').split(","))
    kwargs['task_instance'].xcom_push(key='jobs', value=job_list)


def bq_delete_data(project, dataset, relevant_tables, **kwargs):
    client = bigquery.Client(project=project)
    if not relevant_tables:
        relevant_tables = list(client.list_tables(dataset=dataset))
    for t in relevant_tables:
        table = client.get_table(t)
        client.delete_table(table)  # doesn't return anything


def bq_upload_from_gcs(project, dataset, table, file_uri, **kwargs):
    client = bigquery.Client(project=project, location='EU')
    table_full_name = f'{project}.{dataset}.{table}'
    table_schema = [bigquery.schema.SchemaField(name='date', field_type='DATE'),
                    bigquery.schema.SchemaField(name='ticker', field_type='STRING'),
                    bigquery.schema.SchemaField(name='pred', field_type='FLOAT64')]
    table_obj = bigquery.table.Table(table_full_name, schema=table_schema)
    client.create_table(table_obj)
    job_config = bigquery.job.LoadJobConfig()
    job_config.skip_leading_rows = 1
    try:
        job = client.load_table_from_uri(file_uri, table_full_name, job_config=job_config)
        job.result()
    except Exception as e:
        client.delete_table(table_obj)
        raise e


def create_inference_dataset_for_backfill(obs_date=None):
    sql = Path(os.path.join(SQL_PATH, 'create_inference_dataset.sql')).read_text().replace('?', obs_date)
    bqclient = bigquery.Client()

    bqclient.query(sql).result()


def bq_data_sync(project, dataset, relevant_tables, data_gcs_path, enable_sharding=False, **kwargs):
    extract_jobs = helpers._bq_data_sync(project, dataset, relevant_tables, data_gcs_path, enable_sharding)
    kwargs['task_instance'].xcom_push(key='jobs', value=extract_jobs)


def delete_data_from_gcs(data_gcs_path, **kwargs):
    shards = data_gcs_path.split("/")
    client = storage.Client()
    bucket = client.get_bucket(shards[2])
    blobs = list(bucket.list_blobs(prefix='/'.join(shards[3:])))
    for blob in blobs:
        blob.delete()


def data_sync(cmd, **kwargs):
    output = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    if output.returncode != 0:
        print(output.returncode)
        print(output.stderr)
        return output.stderr
    (value, uom) = output.stderr.decode('utf-8').split("/")[-1].replace("\n", "").strip()[0:-1].split(" ")
    if uom == 'GiB':
        value_gb = float(value)
    elif uom == 'MiB':
        value_gb = float(value) / 1e3
    elif uom == 'KiB':
        value_gb = float(value) / 1e6
    elif uom == 'B':
        value_gb = float(value) / 1e9
    else:
        raise ValueError(f"Unrecognised UOM: {uom}")
    kwargs['task_instance'].xcom_push(key='data_volume_gb', value=value_gb)


def run_gcloud(cmd):
    output = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    if output.returncode != 0:
        print(output.returncode)
        print(output.stderr)
        return output.stderr


def sql_branching(cmd, mode='train_eval', **kwargs):
    output = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    folders = output.stdout.decode('utf-8').replace('/', '').split("\n")[0:-1]
    callables_logger.info(f"Folders found: {folders}")
    if 'sql' in folders:
        if mode == 'train_eval':
            return 'bq-execution-train'
        elif mode == 'inference':
            return 'bq-execution-inference'
        else:
            raise ValueError(f"mode should be either 'train_eval' or 'inference'. Got {mode}.")
    else:
        if mode == 'train_eval':
            return ['sync-train-data-bq-gcs', 'sync-eval-data-bq-gcs']
        elif mode == 'inference':
            return ['sync-inference-data-bq-gcs', 'sync-inference-data-bq-gcs']
        else:
            raise ValueError(f"mode should be either 'train_eval' or 'inference'. Got {mode}.")


def create_disk(project_id, zone, name, size, type, **kwargs):
    # zone = kwargs['task_instance'].xcom_pull(task_ids='choose-compute-zone', value='zone')

    helpers.create_disk(project_id, zone, name, size, type)

    # XCom
    kwargs['task_instance'].xcom_push(key='disk-type', value=type.split("/")[-1])
    kwargs['task_instance'].xcom_push(key='disk-size', value=size)
    kwargs['task_instance'].xcom_push(key='zone', value=zone)


def create_instance(
        project_id,
        zone,
        instance_name,
        machine_type,
        source_image="projects/debian-cloud/global/images/family/debian-10",
        vault_network=False,
        additional_disks=[],
        add_external_ip=False,
        service_account=False,
        startup_script=None,
        challenge_dict=None,
        challenge=None,
        **kwargs
) -> compute_v1.Instance:
    # zone = kwargs['task_instance'].xcom_pull(task_ids='choose-compute-zone', value='zone')

    if service_account:
        sa_specs = {'email': f"aix-worker@{challenge_dict[challenge]['project_name']}.iam.gserviceaccount.com",
                    'scopes': ['https://www.googleapis.com/auth/cloud-platform']}
    else:
        sa_specs = None

    if vault_network:
        network_name = f"global/networks/{challenge_dict[challenge]['network']}"
    else:
        network_name = "global/networks/default"

    operation = helpers.create_instance(project_id, zone, instance_name, machine_type, source_image, network_name,
                                        additional_disks,
                                        add_external_ip, sa_specs, startup_script)

    if operation.error:
        if 'ZONE_RESOURCE_POOL_EXHAUSTED' in str(operation.error):
            kwargs['task_instance'].xcom_push(key='exhausted-zone', value=zone)
        if 'QUOTA_EXCEEDED' in str(operation.error):
            kwargs['task_instance'].xcom_push(key='quota-exceeded-zone', value=zone)
        raise ValueError

    # Sleep for 10 seconds to allow proper SSH initialization on instance
    time.sleep(10)

    # XCom
    kwargs['task_instance'].xcom_push(key='machine-type', value=machine_type)
    kwargs['task_instance'].xcom_push(key='zone', value=zone)


def artifact_quality_assurance(**kwargs):

    # Test at least one artifact exists in process output
    artifacts_gcs_path = kwargs['task_instance'].xcom_pull(task_ids='publish-run-parameters', key='artifacts_gcs_path')
    process_artifact_status, process_artifact_checks = helpers.check_artifact_structure(artifacts_gcs_path, 'models')

    # Test transform output structure
    eval_gcs_path = kwargs['task_instance'].xcom_pull(task_ids='publish-run-parameters', key='evaluation_gcs_path')
    transform_artifact_status, transform_artifact_checks = helpers.check_artifact_structure(eval_gcs_path,
                                                                                            'predictions')

    # Create "quality assurance" artifact (will enable to join current round)
    code_gcs_path = kwargs['task_instance'].xcom_pull(task_ids='publish-run-parameters', key='code_gcs_path')
    challenge = kwargs['task_instance'].xcom_pull(task_ids='publish-run-parameters', key='challenge')
    if process_artifact_status and transform_artifact_status:
        helpers.create_artifact_quality_certificate(code_gcs_path, challenge)
    else:
        helpers.create_artifact_issue_report(code_gcs_path, challenge,
                                             process_artifact_checks, transform_artifact_checks)


def manage_zone_resource_pool_exhaustion(parent_tasks, dag_name, dag_configuration_keys, max_dag_retries,
                                         challenge_dict, **kwargs):
    for task in parent_tasks:
        callables_logger.info(f"Checking task {task}...")

        # Check zonal exhaustion
        exhausted_zone = kwargs['task_instance'].xcom_pull(task_ids=task, key='exhausted-zone')
        callables_logger.info(f"Exhausted zone value is {exhausted_zone} for {task}...")
        if exhausted_zone:
            callables_logger.info(f"Found exhausted zone {exhausted_zone} for {task}...")
            helpers.update_exhausted_zones([exhausted_zone])
            conf = helpers.regenerate_dag_config(kwargs['task_instance'], dag_configuration_keys, True)

        # Check resource quotas exhaustion
        quotas_exceeded_zone = kwargs['task_instance'].xcom_pull(task_ids=task, key='quota-exceeded-zone')
        callables_logger.info(f"Quotas exceeded zone value is {quotas_exceeded_zone} for {task}...")
        if quotas_exceeded_zone:
            callables_logger.info(f"Found quotas exceeded zone {quotas_exceeded_zone} for {task}...")
            conf = helpers.regenerate_dag_config(kwargs['task_instance'], dag_configuration_keys)

        if exhausted_zone or quotas_exceeded_zone:
            callables_logger.info(f"DAG retries value is {conf['dag_retries']}")
            callables_logger.info(f"Max retry value is {max_dag_retries}")
            if conf['dag_retries'] <= max_dag_retries:
                # Write dag request if retries admit it
                callables_logger.info("Writing new dag run request...")
                run_id = conf['user_id'] + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                helpers.write_dag_run_request(dag=dag_name, run_id=run_id,
                                              conf=conf, project=challenge_dict['project_name'],
                                              bucket_name=challenge_dict['bucket'])
                return


def get_inactive_users(challenge, **kwargs):
    sql_statement = "select bucket_id, user_email, username from user_registry where deleted_on is null"
    results = helpers.run_query(sql_statement)

    storage_client = storage.Client(project=COMMON['website_project_name'])

    d = {}
    for item in results:
        if not bool(list(storage_client.list_blobs(bucket_or_name=item[0], prefix=f'{challenge}/active/'))):
            d[item[1]] = {'bucket_id': item[0], 'username': item[2]}

    kwargs['task_instance'].xcom_push(key='inactive_users', value=d)


def reminder_via_email(challenge, until, **kwargs):
    d = kwargs['task_instance'].xcom_pull(task_ids='inactive-users', key='inactive_users')

    with open(os.path.join(PATH, 'config/email.yaml'), 'r') as f:
        config = safe_load(f)

    helpers.reminder_via_email(config, d, challenge, until)


def heartbeat_via_email(**kwargs):

    d = {'admin@ai-exchange.io': True}

    with open(os.path.join(PATH, 'config/email.yaml'), 'r') as f:
        config = safe_load(f)

    helpers.heartbeat_via_email(config, d)


def notify_via_email(user_id, dag, task_instance_list, zonal_exhaustion_task_list, challenge, **kwargs):
    d = {}
    for task in task_instance_list:
        callables_logger.info(f"Recoding state {task.state} for task {task.task_id}...")
        d[task.task_id] = task.state
        if task.task_id in zonal_exhaustion_task_list:
            if kwargs['task_instance'].xcom_pull(task_ids=task.task_id, key='exhausted-zone') or \
                    kwargs['task_instance'].xcom_pull(task_ids=task.task_id, key='quota-exceeded-zone'):
                # Found exhausted zone. Another dag run will start. Skip email notification.
                return

    if dag.endswith('_user_job'):
        if 'failed' in d.values() or 'upstream_failed' in d.values():
            notification_type = 'user_job_failure'
        else:
            notification_type = 'user_job_success'
    else:
        raise NotImplementedError

    with open(os.path.join(PATH, 'config/email.yaml'), 'r') as f:
        config = safe_load(f)

    helpers.send_email(api_key=config['api_key'],
                       from_email=config[notification_type]['from_email'],
                       to_emails=helpers.get_user_email(user_id),
                       subject=config[notification_type]['subject'],
                       html_content=Template(config[notification_type]['html_content']).render(challenge=challenge))


def trigger_user_requests(project, bucket, active):

    if active:
        # Read file(s) from bucket
        client = storage.Client(project)
        request_list = list(client.list_blobs(bucket_or_name=bucket, prefix='user_requests'))

        # Build & run trigger
        for item in request_list:
            run_id = item.name.split("/")[-1]
            dag_name = item.name.split("/")[-2]
            conf = item.download_as_text()
            cmd = f"airflow dags trigger --conf \'{conf}\' --run-id {run_id} {dag_name}"
            dag_status = subprocess.run(cmd, shell=True, capture_output=True)
            if dag_status.returncode != 0:
                callables_logger.error(f"{dag_name} {run_id} trigger failed. \n {dag_status.stderr}")
            else:
                callables_logger.info(f"{dag_name} {run_id} triggered successfully.")
                item.delete()
            time.sleep(1)  # DAGs triggered too quickly end up in internal errors

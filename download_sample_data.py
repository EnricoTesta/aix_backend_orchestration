from helpers import _bq_data_sync

GCS_PATH_ROOT = 'gs://aix-data-stocks-bucket/sample_data_download/'
PROJECT = 'aix-backend-prod'
DATASET = 'stocks_sample_data'
TABLES = ['d_holdout', 'd_inference', 'd_train', 'p_perimeter', 'prices', 't_target']

# BQ to GCS
_bq_data_sync(PROJECT, DATASET, [], GCS_PATH_ROOT, True)

from google.cloud.bigquery import Client, CopyJob, DatasetReference, TableReference, CopyJobConfig
from datetime import datetime as dt

SOURCE_PROJECT = 'aix-data-stocks'
DESTINATION_PROJECT = 'aix-data-stocks-dev'

source_client = Client(project=SOURCE_PROJECT)
destination_client = Client(project=DESTINATION_PROJECT)

source_datasets = source_client.list_datasets()
source_tables = {}
for ds in source_datasets:

    source_table_list = source_client.list_tables(dataset=ds)
    for source_table in source_table_list:
        destination_table_ref = TableReference(dataset_ref=DatasetReference(project=DESTINATION_PROJECT,
                                                                            dataset_id=ds.dataset_id),
                                               table_id=source_table.table_id)
        cj_config = CopyJobConfig()
        cj_config.write_disposition = 'WRITE_TRUNCATE'
        print(f"Copying table {SOURCE_PROJECT}.{ds.dataset_id}.{source_table.table_id} to {DESTINATION_PROJECT}...")
        cj = CopyJob(client=destination_client,
                     job_id=f'cj-{dt.utcnow()}'.replace(':', '').replace('.', '').replace(' ', ''),
                     sources=[source_table.reference], destination=destination_table_ref, job_config=cj_config)
        cj.result()  # start and wait to finish
        print("Done")

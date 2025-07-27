from google.cloud.bigquery import Client, DatasetReference, Dataset


SOURCE_PROJECT = 'aix-data-stocks'
DESTINATION_PROJECT = 'aix-data-stocks-dev'

source_client = Client(project=SOURCE_PROJECT)
destination_client = Client(project=DESTINATION_PROJECT)

source_user_datasets = [ds for ds in source_client.list_datasets() if ds.dataset_id.startswith('ud_')]

for ds in source_user_datasets:
    print(f"Copying {SOURCE_PROJECT}.{ds.dataset_id} to {DESTINATION_PROJECT}...")
    new_dataset = Dataset(f'{DESTINATION_PROJECT}.{ds.dataset_id}')
    try:
        destination_client.delete_dataset(new_dataset, delete_contents=True)
        print(f"Deleting {DESTINATION_PROJECT}.{ds.dataset_id}...")
    except:
        pass
    new_dataset.location = 'EU'
    destination_client.create_dataset(new_dataset)
    print("Done")

from google.cloud.storage import Client, Bucket


SOURCE_PROJECT = 'aix-website-prod'
DESTINATION_PROJECT = 'aix-website-dev'
SUFFIX = '_dev'

source_client = Client(project=SOURCE_PROJECT)
#destination_client = Client(project=DESTINATION_PROJECT)

source_user_buckets = [b for b in source_client.list_buckets() if b.name.startswith('202')]

for b in source_user_buckets:
    print(f"Copying {b.name} to {DESTINATION_PROJECT} adding suffix {SUFFIX}...")
    new_bucket = Bucket(f'{b.name}{SUFFIX}')
    new_bucket.location = 'EU'
    new_bucket.storage_class = 'STANDARD'
    #destination_client.create_bucket(new_bucket)
    print("Done")

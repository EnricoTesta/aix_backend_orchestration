from airflow.sensors.base import BaseSensorOperator
from google.cloud import storage
import google.cloud.compute_v1 as compute_v1


class VMShutdownSensorOperator(BaseSensorOperator):
    template_fields = ["poke_kwargs"]

    def __init__(self, poke_kwargs, **kwargs):
        super().__init__(**kwargs)
        self.poke_kwargs = poke_kwargs

    def poke(self, context) -> bool:
        instance_client = compute_v1.InstancesClient()
        instance_req = compute_v1.types.GetInstanceRequest()
        instance_req.instance = self.poke_kwargs['instance_name']
        instance_req.zone = self.poke_kwargs['zone']
        instance_req.project = self.poke_kwargs['project']

        instance = instance_client.get(request=instance_req)
        if instance.status == 'TERMINATED':
            return True
        return False


class InferenceSensorOperator(BaseSensorOperator):
    template_fields = ["poke_kwargs"]

    def __init__(self, poke_kwargs, **kwargs):
        super().__init__(**kwargs)
        self.poke_kwargs = poke_kwargs

    def poke(self, context) -> bool:

        storage_client = storage.Client()
        jobs = context['task_instance'].xcom_pull(task_ids=['trigger-inference-jobs'], key='active_inference')[0]
        scored_jobs = [item.name.split("/")[-2] for item in
                       list(storage_client.list_blobs(bucket_or_name=self.poke_kwargs['bucket'],
                                                      prefix=self.poke_kwargs['prefix']))]
        print(jobs)
        print(scored_jobs)
        for job in jobs:
            if job not in scored_jobs:
                return False
        return True

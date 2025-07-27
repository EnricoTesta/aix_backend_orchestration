CREATE TABLE IF NOT EXISTS cloud_usage (
    task_id varchar(30) NOT NULL,
    user_id char(28) NOT NULL,
    workflow_id varchar(43) NOT NULL,
    job_id varchar(36) NOT NULL, -- some tasks process multiple jobs
    registry_timestamp timestamp NOT NULL,
    resource_id smallint NOT NULL,
    zone varchar(20) NOT NULL,
    uptime_seconds int NOT NULL, -- seconds
    volume_gb numeric, -- only for data transfer
    PRIMARY KEY (task_id, user_id, workflow_id, job_id)
    );

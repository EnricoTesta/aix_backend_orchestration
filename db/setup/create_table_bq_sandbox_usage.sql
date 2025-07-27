CREATE TABLE IF NOT EXISTS bq_sandbox_usage (
    job_id char(28) NOT NULL,
    user_email varchar(50) NOT NULL,
    location char(2) NOT NULL,
    resource_id smallint NOT NULL,
    start_timestamp timestamp NOT NULL,
    end_timestamp timestamp NOT NULL,
    total_bytes bigint NOT NULL,
    PRIMARY KEY (job_id, user_email, resource_id)
);
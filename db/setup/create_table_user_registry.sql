CREATE TABLE IF NOT EXISTS user_registry (
    user_id char(28) PRIMARY KEY,
    user_email varchar(50) NOT NULL,
    username varchar(15) NOT NULL,
    created_on timestamp NOT NULL,
    deleted_on timestamp,
    bucket_id char(43) NOT NULL,
    dataset_id char(13) NOT NULL
    );
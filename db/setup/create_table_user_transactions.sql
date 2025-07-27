CREATE TABLE IF NOT EXISTS user_transactions (
    user_id varchar(28) NOT NULL,
    workflow_id varchar(41) NOT NULL,
    workflow_type varchar(20),
    currency char(3) NOT NULL,
    external_transaction_id varchar(20),
    transaction_timestamp timestamp NOT NULL,
    transaction_side bool NOT NULL, -- buy/sell
    transaction_type varchar(10) NOT NULL, -- top-up, cloud cost, revenue
    amount numeric NOT NULL,
    PRIMARY KEY (user_id, workflow_id)
    );
CREATE TABLE IF NOT EXISTS prize_pool (
    ref_date date NOT NULL,
    problem_id varchar(28) NOT NULL,
    amount int NOT NULL,
    PRIMARY KEY (ref_date, problem_id)
    );
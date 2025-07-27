CREATE TABLE IF NOT EXISTS prize_assignment (
    ref_date date NOT NULL,
    problem_id varchar(28) NOT NULL,
    user_id char(28) NOT NULL,
    prize_percentage numeric NOT NULL,
    PRIMARY KEY (ref_date, problem_id, user_id)
    );
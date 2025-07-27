create table if not exists t_web_user_leaderboard (
    user_id char(28) NOT NULL,
    challenge varchar(28) NOT NULL,
    ref_date date NOT NULL,
    weight numeric NOT NULL,
    prize numeric NOT NULL,
    PRIMARY KEY (user_id, challenge)
);
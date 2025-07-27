create table if not exists t_web_user_current_credits_and_wallet (
    user_id char(28) PRIMARY KEY,
    credits numeric,
    wallet numeric
);
create or replace procedure user_top_up(transaction_id character varying, user_id character varying, amount numeric, currency char(3), t_timestamp timestamp)
language sql
as $$
insert into user_transactions values (user_id, concat('topup-', cast(t_timestamp as text)), 'top-up', currency, transaction_id, t_timestamp, true, 'top-up', amount)
$$;
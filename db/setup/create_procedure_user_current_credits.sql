create or replace procedure user_current_credits_and_wallet()
language plpgsql as $$
begin
truncate table t_web_user_current_credits_and_wallet;
insert into t_web_user_current_credits_and_wallet
select ur.user_id
     , coalesce(sum(case when transaction_type in ('top-up', 'cloud-cost') then
            case when transaction_side is true then amount else -amount end
           else 0 end), 0) as credits
     , coalesce(sum(case when transaction_type not in ('top-up', 'cloud-cost') then
            case when transaction_side is true then amount else -amount end
           else 0 end), 0) as wallet
from user_registry ur
left join user_transactions ut
on ur.user_id = ut.user_id
group by 1;
end
$$;
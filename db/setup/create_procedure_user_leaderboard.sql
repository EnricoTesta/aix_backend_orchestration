create or replace procedure user_leaderboard()
language plpgsql as $$
begin
truncate table t_web_user_leaderboard;
insert into t_web_user_leaderboard
select ur.username
 , problem_id as challenge
 , cast(substring(workflow_id, 7) as date) as ref_date
 , prize_percentage as weight
 , amount as prize
from user_registry ur
left join user_transactions ut
on ur.user_id = ut.user_id
left join prize_assignment pa
on ur.user_id = pa.user_id
and cast(substring(ut.workflow_id, 7) as date) = pa.ref_date
where ut.transaction_type = 'prize'
and substring(ut.workflow_id, 7) = (select max(substring(workflow_id, 7)) from user_transactions where transaction_type = 'prize')
order by amount desc;
end
$$;
select user_id
, round(prize_percentage * amount, 2) as amount
from prize_assignment pa
join prize_pool pp
on pa.ref_date = pp.ref_date
and pa.problem_id = pp.problem_id
where pa.ref_date = '{{reference_date}}'
and pa.problem_id = '{{problem_identifier}}'
create or replace procedure update_user_transactions() language sql as $$
with cloud_usage_transactions as (
	select *
	, case when resource_id between 1 and 100 then cast(uptime_seconds as float)/3600 * cost_per_unit -- VM
		   when resource_id between 101 and 200 then cast(uptime_seconds as float)/case when unit='hour' then 3600 when unit='month' then 3600*28 end * cost_per_unit -- disk
		   when resource_id = 201 then volume_gb * cost_per_unit -- data-transfer
		   when resource_id = 301 then volume_gb/1e3 * cost_per_unit -- BQ processing (cost is per TB)
		   when resource_id = 302 then volume_gb * 1/(cast(uptime_seconds as float)*3600*28) * cost_per_unit -- BQ storage (!!! uptime second not representative of table's life span !!!)
	end as cloud_cost
	, case when resource_id between 1 and 100 then cast(uptime_seconds as float)/3600 * bill_per_unit -- VM
		   when resource_id between 101 and 200 then cast(uptime_seconds as float)/case when unit='hour' then 3600 when unit='month' then 3600*28 end * bill_per_unit -- disk
		   when resource_id = 201 then volume_gb * bill_per_unit -- data-transfer
		   when resource_id = 301 then volume_gb/1e3 * bill_per_unit -- BQ processing (cost is per TB)
		   when resource_id = 302 then volume_gb * 1/(cast(uptime_seconds as float)*3600*28) * bill_per_unit -- BQ storage (!!! uptime second not representative of table's life span !!!)
	end as cloud_billable
	from cloud_usage cu
	left join dim_cloud_resource dcr
	using(resource_id, zone)
	where registry_timestamp > (select coalesce(max(transaction_timestamp), cast('2000-01-01' AS timestamp)) from user_transactions where workflow_type not in ('bq-sandbox', 'top-up', 'prize'))
)
, bq_sandbox_transactions as (
	select user_id
	, bsu.resource_id
	, currency
	, start_timestamp
	, end_timestamp
	, case when bsu.resource_id = 301 then total_bytes/1e12 * cost_per_unit
		   when bsu.resource_id = 302 then total_bytes/1e9 * cost_per_unit * DATE_PART('day', end_timestamp - start_timestamp)/30 end as cloud_cost
	, case when bsu.resource_id = 301 then total_bytes/1e12 * bill_per_unit
		   when bsu.resource_id = 302 then total_bytes/1e9 * bill_per_unit * DATE_PART('day', end_timestamp - start_timestamp)/30 end as cloud_billable
	from bq_sandbox_usage bsu
	left join dim_cloud_resource dcr
	on bsu.resource_id = dcr.resource_id
	left join user_registry ur
	on bsu.user_email = ur.user_email
	where start_timestamp > (select coalesce(max(transaction_timestamp), cast('2000-01-01' AS timestamp)) from user_transactions where workflow_type = 'bq-sandbox')
	-- (!!!) This does not consider all jobs started @ a specific date but not yet completed before usage sensor pass. Could use estimated bytes instead of billed bytes.
)
, full_transactions as (
	select user_id
	, workflow_id
	, 'user-job' as workflow_type
	, currency
	, registry_timestamp as transaction_timestamp
	, False as transaction_side -- cost for the user
	, 'cloud-cost' as transaction_type
	, sum (cloud_cost) as cloud_cost
	, sum (cloud_billable) as cloud_billable
	from cloud_usage_transactions
	group by 1, 2, 3, 4, 5, 6
	union all
	select user_id
	, concat('bq_sandbox-', cast (date_trunc('day', start_timestamp) as char (10))) as workflow_id
	, 'bq-sandbox' as workflow_type
	, currency
	, max(start_timestamp) as transaction_timestamp
	, False as transaction_side -- cost for the user
	, 'cloud-cost' as transaction_type
	, sum (cloud_cost) as cloud_cost
	, sum (cloud_billable) as cloud_billable
	from bq_sandbox_transactions
	group by 1, 2, 3, 4, 6
)
insert into user_transactions
select user_id
     , workflow_id
     , workflow_type
     , currency
     , null as external_transaction_id
     , transaction_timestamp
     , transaction_side
     , transaction_type
     , round(cast(ceil(cloud_billable*100)/100 as numeric), 2) as amount
from full_transactions
$$;
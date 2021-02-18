create view if not exists summary_status_name as 
select distinct 
    name,
    status, 
    count(*) as count 
from transactions 
group by 
    name,
    status
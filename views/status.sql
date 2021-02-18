create view if not exists summary_status as 
select distinct 
    status, 
    count(*) as count 
from transactions 
group by status
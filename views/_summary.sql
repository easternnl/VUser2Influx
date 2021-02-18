CREATE VIEW IF NOT EXISTS _summary AS 
select 
    name,
    percentile(responsetime, 95) as percentile95, 
    avg(responsetime) as avg, 
    max(responsetime) as max, 
    min(responsetime) as min, 
    count(responsetime) as count 
from alltransactions 
where 
    type='transaction' and 
    responsetime > -1 
group by 
    name 
order by 
    name, avg desc;
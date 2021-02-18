CREATE VIEW IF NOT EXISTS _summary_cache AS 
select 
    name,
    extra,
    case cache when 1 then "cached" else "1stvisit" end as cache ,
    percentile(responsetime, 90) as percentile90, 
    avg(responsetime) as avg , 
    max(responsetime) as max , 
    min(responsetime) as min, 
    count(responsetime) as count 
from alltransactions 
where 
    type='transaction'  
    and responsetime > -1  
group by 
    name,
    extra,
    cache 
order by 
    name,
    extra,
    cache desc;
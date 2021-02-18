CREATE VIEW IF NOT EXISTS responsetime_of_vuser as 
select 
    vuser, 
    sum(responsetime) as responsetime 
from alltransactions 
where 
    type = 'transaction' 
group by 
    vuser;
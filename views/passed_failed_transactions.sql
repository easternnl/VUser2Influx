-- Filter the passed and failed transactions from the transaction table.
--
-- TODO: Fix the responsetime = -1 to something else. This is mainly used in the LoadRunner importer.
-- 
CREATE VIEW IF NOT EXISTS passed_failed_transactions as 
select 
    name,   
    count(
        case 
             when responsetime = -1 then 'Failed'
             when status = '500' then 'Failed'
             else null  
        end    )
        as Failed,  
    count(
        case 
             when status != '500' then 'Passed'
--             when responsetime > -1 then 'Passed'                 
             else null    
        end    )
        as Passed,
    count(*) as Total 
from alltransactions 
where type='transaction' 
group by name;
CREATE VIEW IF NOT EXISTS _faulty_transactions as 
select 
    * 
from alltransactions 
where (
    responsetime = -1 or 
    status = 500
    );
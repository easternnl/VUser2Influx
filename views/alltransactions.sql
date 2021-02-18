CREATE VIEW IF NOT EXISTS alltransactions as 
select 
    id, 
    name, 
    type, 
    datetime(starttime_epoch, 'unixepoch', 'localtime') as starttime,
    starttime_epoch, 
    datetime(stoptime_epoch, 'unixepoch', 'localtime') as stoptime,
    stoptime_epoch,
    responsetime,
    user,
    status,
    iteration,
    vuser,
    cache,
    extra,
    failmsg,
    URL,
    response,
    runningvusers 
from transactions;
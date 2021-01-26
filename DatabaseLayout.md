# Database layout

- id
- starttime_epoch
- stoptime_epoch
- responsetime
- user
- status
- iteration
- cache
- vuser
- extra
- error
- URL
- response
- runningvusers

# File Layouts with mapping to database

## JTL

- timeStamp = starttime_epoch
- elapsed = responsetime
- label = name
- responseCode = status
- responseMessage = <response>
- threadName = VUser
- dataType = {SKIP}
- success = status
- failureMessage = error
- bytes	={SKIP}
- sentBytes = {SKIP}
- grpThreads = {SKIP}
- allThreads=<runningvusers>
- URL = <URL>
- Latency = {SKIP}
- IdleTime = {SKIP}
- Connect = {SKIP}

# Old database layout (pre 2021) 

- id
- name
- type
- starttime_epoch
- stoptime_epoch
- responsetime
- user
- status
- iteration
- cache
- vuser
- extra
- error



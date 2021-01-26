# Database layout

id INTEGER PRIMARY KEY  
name VARCHAR(40)  
starttime_epoch REAL  
stoptime_epoch REAL  
responsetime REAL  
user  
type VARCHAR(10)  
status  
iteration INTEGER  
cache INTEGER  
vuser  
extra  
error  
URL  
response  
runningvusers  

```
CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY ,name varchar(40), type varchar(10), starttime_epoch REAL, stoptime_epoch REAL, responsetime REAL, user, status, iteration INTEGER, cache INTEGER, vuser, extra, error)')
```

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

- id INTEGER PRIMARY KEY
- name VARCHAR(40)
- type VARCHAR(10)
- starttime_epoch REAL
- stoptime_epoch REAL
- responsetime REAL
- user
- status
- iteration INTEGER
- cache INTEGER
- vuser
- extra
- error

```
CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY ,name varchar(40), type varchar(10), starttime_epoch REAL, stoptime_epoch REAL, responsetime REAL, user, status, iteration INTEGER, cache INTEGER, vuser, extra, error)')
```




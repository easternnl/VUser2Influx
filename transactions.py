import re
import time
import datetime
import operator # use for sorting arrays
from pytz import timezone
from influxdb import InfluxDBClient
from datetime import timedelta

# defenition of a transaction
class transactiontype:
    count = 0

    def __init__(self, starttime_epoch, stoptime_epoch, trans, user, resptime, status, iteration, vuser, extra, typetransaction):
        self.starttime_epoch = starttime_epoch
        self.stoptime_epoch = stoptime_epoch
        self.trans = trans
        self.user = user
        self.resptime = resptime
        self.status = status
        self.iteration = iteration
        self.vuser = vuser
        self.extra = extra
        self.type = typetransaction

        transactiontype.count += 1

    def VUserLog(filename):
        transactions = []

        with open(filename) as fp:  
            for cnt, line in enumerate(fp):
                # reset all variabeles
                epoch = 0       
                trans = ""
                user = ""
                resptime = 0
                status = 0
                iteration = 0
                vuser = 0
                extra = ""
                
                # search for an epoch timestamp in the file
                #epoch = re.search(r'([0-9]{10,13})', line)
                epoch = re.search(r'([0-9]{10}\.[0-9]{3}|[0-9]{10,13})', line)

                if epoch:   # found a transaction in the log file
                    if len(epoch.group(1)) == 10:     # convert seconds to nanoseconds
                        epoch = float(epoch.group(1)) * 1000 * 1000
                    elif len(epoch.group(1)) == 13:   # convert ms to nanoseconds
                        epoch = float(epoch.group(1)) * 1000
                    elif len(epoch.group(1)) == 14:   # seconds with milliseconds after the dot
                        epoch = float(epoch.group(1)) * 1000 * 1000
                    
                    #print ("epoch=%d" % (epoch))        
                    pattern = re.compile(r'(\w+)=([^,|\s]+)')
                    for (key, value) in re.findall(pattern, line):
                        if key == "name" or key=="trans":
                            if "action" in value:
                                typetransaction = "action"
                            else:
                                typetransaction = "transaction"
                            trans = value
                        elif key == "user":
                            user = value
                        elif key == "resptime":
                            resptime = float(value)
                        elif key == "status":
                            status = value
                        elif key == "iteration":
                            iteration = float(value)
                        elif key == "vuser":
                            vuser = float(value)
                        elif key == "extra":
                            extra = value
                        
                        #print("%s=%s" % (key, value))

                    if resptime == -1 and trans:
                        # add a transaction to the list

                        # print("OPEN epoch=%d trans=%s user=%s resptime=%s status=%s iteration=%s vuser=%s extra=%s" % (epoch, trans, user, resptime, status, iteration, vuser, extra))
                        #print("OPEN epoch=%d trans=%s user=%s resptime=%f status=%s iteration=%s vuser=%s extra=%s" % (epoch, trans, user, resptime, status, iteration, vuser, extra))

                        transactions.append(transactiontype(epoch, 0, trans, user, resptime, status, iteration, vuser, extra, typetransaction))
                                                    
                        
                    elif resptime > 0 and trans:
                        #search for last matching number with trans, user, resptime=-1, iteration, vuser, extra and adjust the resptime                

                        print ("scanning for: trans=%s user=%s resptime=-1 iteration=%s vuser=%s extra=%s" % (trans, user, iteration, vuser, extra))

                        for transaction in reversed(transactions):
                            # verify if this is the same transaction
                            print ("    current: trans=%s user=%s resptime=-1 iteration=%s vuser=%s extra=%s" % (transaction.trans, transaction.user, transaction.iteration, transaction.vuser, transaction.extra))
                            if transaction.trans == trans and transaction.user == user and transaction.resptime == -1 and transaction.iteration == iteration and transaction.vuser == vuser and transaction.extra == extra and transaction.type == typetransaction:
                                print("        Last transaction: name=%s, resptime=%s, epoch=%s" % (transaction.trans, transaction.resptime, transaction.starttime_epoch))
                                print("        Current transaction: name=%s, resptime=%s, epoch=%s" % (trans, resptime, epoch))
                                transaction.resptime = resptime
                                transaction.stoptime_epoch = epoch
                                transaction.status = status
                                break

        return transactions        

    def Send2SQLite(self, filename, dropdatabase):
        import sqlite3

        conn = sqlite3.connect(filename)
        c = conn.cursor()

        if dropdatabase:
            c.execute('drop table if exists transactions;')

        # setup the database with all default tables
        c.execute('create table if not exists transactions(id INTEGER PRIMARY KEY ,name varchar(40), type varchar(10), starttime_epoch REAL, stoptime_epoch REAL, responsetime REAL, user, status, iteration INTEGER, vuser, extra, error)')

        # setup the database with all default views
        c.execute("CREATE VIEW IF NOT EXISTS _summary AS select name,percentile(responsetime, 95) as percentile95, avg(responsetime) as avg , max(responsetime) as max , min(responsetime) as min, count(responsetime) as count from transactions where type='transaction'  and responsetime > -1  group by name order by avg desc;")
        c.execute("CREATE VIEW IF NOT EXISTS alltransactions as select id, name, type, datetime(starttime_epoch, 'unixepoch', 'localtime') as starttime,starttime_epoch, datetime(stoptime_epoch, 'unixepoch', 'localtime') as stoptime,stoptime_epoch,responsetime,user,status,iteration,vuser,extra from transactions;");
        c.execute("CREATE VIEW IF NOT EXISTS _faulty_transactions as select * from alltransactions where responsetime = -1;");
        # create view for calculating responsetime	
        c.execute("CREATE VIEW IF NOT EXISTS _calculatedresponsetime as select *, [stoptime_epoch] - [starttime_epoch] as responsetimecalc from alltransactions;");
        # create summary view with calculated responsetimes for using with LR 12.55 with TruClient Chromium - this version is not reporting response times in Javascript
        c.execute("create view if not exists _summarycalculated as select name,percentile(responsetimecalc, 95) as percentile95, avg(responsetimecalc) as avg , max(responsetimecalc) as max , min(responsetimecalc) as min, count(responsetimecalc) as count from _calculatedresponsetime where type='transaction'  and responsetime > -1  group by name order by avg desc;");
        c.execute("CREATE VIEW IF NOT EXISTS passed_failed_actions as select name,   count(case     when responsetime = -1 then 'Failed'    else null    end    )as Failed,  count(case     when responsetime > -1 then 'Passed'    else null    end    )as Passed from transactions where type='action' group by name;");
        c.execute("CREATE VIEW IF NOT EXISTS passed_failed_transactions as select name,   count(case     when responsetime = -1 then 'Failed'    else null    end    )as Failed,  count(case when responsetime > -1 then 'Passed'    else null    end    )as Passed from transactions where type='transaction' group by name;");
        c.execute("CREATE VIEW IF NOT EXISTS responsetime_of_actions AS select name, vuser, responsetime from transactions where  type ='action' group by vuser, name order by vuser, starttime;");
        c.execute("CREATE VIEW IF NOT EXISTS responsetime_of_vuser as select vuser, sum(responsetime) as responsetime from transactions where type = 'transaction' group by vuser;");
        c.execute("CREATE VIEW IF NOT EXISTS testduration as select datetime(min(starttime_epoch), 'unixepoch', 'localtime') as starttimetest, datetime(max(stoptime_epoch), 'unixepoch', 'localtime') as stoptimetest, max(stoptime_epoch) - min(starttime_epoch) as duration_seconds, (max(stoptime_epoch) - min(starttime_epoch)) / 60 as duration_minutes from transactions;");

        c.execute("CREATE INDEX UpdateQueryLRLogs ON transactions(name, user, vuser, iteration, stoptime_epoch)");

        # insert all the transactions into the database
        for transaction in self:            
            print ("SQLite: %s" % (transaction.SqLite()))
            c.execute(transaction.SqLite())
            
        # Save (commit) the changes
        conn.commit()

        conn.close()

        return


    def SqLite(self):
        # return SQL insert statement for the current transaction
        return "INSERT INTO Transactions( name, type, starttime_epoch, stoptime_epoch, responsetime, user, iteration, status, vuser, extra) VALUES ('%s', '%s', %d, %d,  %6f, '%s', %d, '%s', %d, '%s');" % (self.trans, self.type, self.starttime_epoch / 1000000, self.stoptime_epoch /1000000 , self.resptime, self.user, self.iteration, self.status, self.vuser, self.extra)
			

    
    def InfluxDbLine(self):
        # return the InfluxDb Line statement for the current transaction
        # datapoint = "%s host=%s, instance=%s, objectname=%s %s=%d %d" %(measurement, host, instance, objectname, field, float(value), timestamp )
        return "INSERT INTO transactions (%s)" % ( self.trans)

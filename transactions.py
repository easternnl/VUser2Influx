import re
import time
import datetime
from datetime import datetime
import operator # use for sorting arrays
import glob # used for walking through directories
import os
from pytz import timezone
from influxdb import InfluxDBClient
from datetime import timedelta

##
## Check if data type of field is float
##
def isfloat(value):
        try:
            float(value)
            return True
        except:
            return False

##
## Check if data type of field is int
##
def isinteger(value):
        try:
            if(float(value).is_integer()):
                return True
            else:
                return False
        except:
            return False

# defenition of a transaction
class transactiontype:
    count = 0

    def __init__(self, starttime_epoch, stoptime_epoch, trans, user, resptime, status, iteration, vuser, extra, typetransaction, cache):
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
        self.cache = cache

        transactiontype.count += 1

    def ImportLogs(self,inputfilter):
        # handle the import of an file based on the extension specified

        # not working yet due to incorrent self assignment
        import os

        transactions = []

        for filename in glob.glob(inputfilter):
            #print("File: %s" % (filename))

            extension = os.path.splitext(filename)[1]

            #print("Extension: %s" % (extension))

            if extension == ".log" or extension == ".txt":
                #print ("VUser log")

                transactions += transactiontype.VUserLog(filename)
            elif extension == ".jtl":
                print ("JMeter results - not finished yet (work in progress)")

                transactions += transactiontype.JMeterLog(filename)
            elif extension == ".tikker":               

                transactions += transactiontype.TikkerLog(filename)
            elif extension == ".db" or extension == ".db3":
                #print ("SQLite for Truweb")

                transactions += transactiontype.TruwebLog(filename)

        return transactions

    def JMeterLog(inputfilter):
        transactions = []

        for filename in glob.glob(inputfilter):
            print("Importing JMeter: %s" % (filename))

            with open(filename) as fp:  
                next(fp)
                for cnt, line in enumerate(fp):
                    jmeter = line.split(',')    

                    epoch = float(jmeter[0]) * 1000 * 1000 
                    stoptime_epoch = epoch + (float(jmeter[1]) * 1000 * 1000 )
                    #stoptime_epoch = 0
                    trans = jmeter[2]
                    user = ""
                    resptime = float(float(jmeter[1]) / 1000)
                    
                    if jmeter[7] == "true":
                        status = 2
                    else:
                        status = 0                        
                    user = ""                   
                    iteration = 0                    
                    vuser = re.search(r'-([0-9]+)', jmeter[5])
                    vuser = int(vuser.group(1))
                    print(vuser)
                    extra = ""
                    typetransaction = "transaction"
                    cache = 0

                    transactions.append(transactiontype(epoch, stoptime_epoch, trans, user, resptime, status, iteration, vuser, extra, typetransaction, cache))

        return transactions

    def TikkerLog(inputfilter):
        transactions = []

        for filename in glob.glob(inputfilter):
            print("Importing Tikkerlog: %s" % (filename))

            #fname = pathlib.Path(filename)
            #date = datetime.fromtimestamp(fname.stat().st_ctime)
            created = os.path.getctime(filename)
            year,month,day=time.localtime(created)[:-6]
            print("Date created: %02d/%02d/%d "%(day,month,year,))

            #print(date)

            with open(filename) as fp:  
                for cnt, line in enumerate(fp):
                    # scan for transaction with timestamp and responsetime
                    tikker = re.search(r'([0-9]{2})h:([0-9]{2})m:([0-9]{2})s,\s([0-9]{1,2}.[0-9]{2})\ss,\s{1,4}(.*)', line)

                    if tikker:   # found a tikker log line with responsetime, starttime and transactionname
                        # reset all variabeles
                        epoch = datetime(year,month,day,int(tikker.group(1)),int(tikker.group(2)), int(tikker.group(3))).timestamp() * 1000 * 1000 * 1000 
                        trans = tikker.group(5)
                        user = ""
                        resptime = float(tikker.group(4))
                        status = 0
                        iteration = 0
                        vuser = 1
                        extra = "Tikker"
                        typetransaction = "transaction"
                        stoptime_epoch = epoch + (resptime * 1000 * 1000 * 1000 )
                        cache = 0
                        
                        print("Name: %s, Responsetime: %s, Starttime: %f" % (tikker.group(5), tikker.group(4), epoch))

                        transactions.append(transactiontype(epoch, stoptime_epoch, trans, user, resptime, status, iteration, vuser, extra, typetransaction, cache))



        return transactions

                    
        
        
    def TruwebLog(inputfilter):
        import sqlite3

        transactions = []

        for filename in glob.glob(inputfilter):
            print("Importing SQLite for Truweb File: %s" % (filename))

            conn = sqlite3.connect(filename)
            c = conn.cursor()

            for row in c.execute('SELECT timestamp, name, duration, status FROM Transactions'):
                #print (row)
                # create all variabeles
                if '.' in row[0]:
                    epoch = datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S.%f').timestamp() * 1000 * 1000 * 1000  
                else:
                    epoch = datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S').timestamp() * 1000 * 1000 * 1000  

                trans = row[1]
                user = ""
                resptime = row[2] / 1000
                if row[3] == "Passed":
                    status = 2
                else:
                    status = 0
                iteration = -1
                vuser = -1
                extra = ""
                typetransaction = "transaction"
                stoptime_epoch = epoch
                starttime_epoch = epoch - (resptime * 1000 * 1000 * 1000)
                cache = 0

                transactions.append(transactiontype(starttime_epoch, stoptime_epoch, trans, user, resptime, status, iteration, vuser, extra, typetransaction, cache))

            conn.close()

        return transactions


    def VUserLog(inputfilter):
        transactions = []

        for filename in glob.glob(inputfilter):
            print("Importing VUserlog: %s" % (filename))
        
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
                    typetransaction = "transaction"
                    cache = 0
                    
                    # search for an epoch timestamp in the file
                    #epoch = re.search(r'([0-9]{10,13})', line)
                    epoch = re.search(r'([0-9]{10}\.[0-9]{3}|[0-9]{10,13})', line)

                    if epoch:   # found a transaction in the log file
                        if len(epoch.group(1)) == 10:     # convert seconds to nanoseconds
                            #print ("Epoch with 10")
                            epoch = float(epoch.group(1)) * 1000 * 1000 * 1000
                        elif len(epoch.group(1)) == 13:   # convert ms to nanoseconds
                            #print ("Epoch with 13")
                            epoch = float(epoch.group(1)) * 1000 * 1000
                        elif len(epoch.group(1)) == 14:   # seconds with milliseconds after the dot
                            #print ("Epoch with 14 (10.3)")
                            epoch = float(epoch.group(1)) * 1000 * 1000 * 1000
                        
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
                                if (status == "Passed"):
                                    status = 2
                                elif (status == "Auto"):
                                    status = 2
                            elif key == "iteration":
                                iteration = float(value)
                            elif key == "vuser":
                                vuser = float(value)
                            elif key == "extra":
                                extra = value
                            elif key == "cache":
                                cache = int(value)
                            
                            #print("%s=%s" % (key, value))

                        if resptime == -1 and trans:
                            # add a transaction to the list

                            # print("OPEN epoch=%d trans=%s user=%s resptime=%s status=%s iteration=%s vuser=%s extra=%s" % (epoch, trans, user, resptime, status, iteration, vuser, extra))
                            #print("OPEN epoch=%d trans=%s user=%s resptime=%f status=%s iteration=%s vuser=%s extra=%s" % (epoch, trans, user, resptime, status, iteration, vuser, extra))

                            transactions.append(transactiontype(epoch, 0, trans, user, resptime, status, iteration, vuser, extra, typetransaction, cache))
                                                        
                            
                        elif resptime > 0 and trans:
                            #search for last matching number with trans, user, resptime=-1, iteration, vuser, extra and adjust the resptime                

                            #print ("scanning for: trans=%s user=%s resptime=-1 iteration=%s vuser=%s extra=%s" % (trans, user, iteration, vuser, extra))

                            for transaction in reversed(transactions):
                                # verify if this is the same transaction
                                #print ("    current: trans=%s user=%s resptime=-1 iteration=%s vuser=%s extra=%s" % (transaction.trans, transaction.user, transaction.iteration, transaction.vuser, transaction.extra))
                                if transaction.trans == trans and transaction.user == user and transaction.resptime == -1 and transaction.iteration == iteration and transaction.vuser == vuser and transaction.extra == extra and transaction.type == typetransaction:
                                    #print("        Last transaction: name=%s, resptime=%s, epoch=%s" % (transaction.trans, transaction.resptime, transaction.starttime_epoch))
                                    #print("        Current transaction: name=%s, resptime=%s, epoch=%s" % (trans, resptime, epoch))
                                    transaction.stoptime_epoch = epoch
                                    transaction.status = status
                                    if resptime == 1.000000:
                                        # calculate the response time based on the 
                                        #print ("Calculation: %f - %f" % (transaction.stoptime_epoch, transaction.starttime_epoch))
                                        transaction.resptime = (transaction.stoptime_epoch - transaction.starttime_epoch) / 1000000000
                                    else:
                                        transaction.resptime = resptime                                    

                                    break

        return transactions        

    def Send2CSV(self, filename):
        # insert all the transactions into the CSV file

        print("Send2CSV: %s" % (filename))

        f = open(filename, "w")

        # print header
        f.write(self[0].CSV(header=1))

        # print detailed transaction information
        for transaction in self:            
            #print ("SQLite: %s" % (transaction.SqLite()))
            f.write(transaction.CSV(header=0))            

    def Send2STT(self, filename):
        # insert all the transactions into the CSV file

        print("Send2STT: %s" % (filename))

        f = open(filename, "w")

        # print detailed transaction information
        for transaction in self:            
            #print ("SQLite: %s" % (transaction.SqLite()))
            f.write(transaction.STT(header=0))            

def Send2SQLite(self, filename, dropdatabase):
        # insert all the transactions into the SQLite database
        print("Send2SQLite: %s" % (filename))

        import sqlite3

        conn = sqlite3.connect(filename)
        c = conn.cursor()

        if dropdatabase:
            c.execute('DROP TABLE IF EXISTS transactions;')

        # setup the database with all default tables
        c.execute('CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY ,name varchar(40), type varchar(10), starttime_epoch REAL, stoptime_epoch REAL, responsetime REAL, user, status, iteration INTEGER, cache INTEGER, vuser, extra, error)')

        # setup the database with all default views
        c.execute("CREATE VIEW IF NOT EXISTS _summary AS select name,percentile(responsetime, 95) as percentile95, avg(responsetime) as avg , max(responsetime) as max , min(responsetime) as min, count(responsetime) as count from alltransactions where type='transaction'  and responsetime > -1  group by name order by avg desc;")
        c.execute("CREATE VIEW IF NOT EXISTS alltransactions as select id, name, type, datetime(starttime_epoch, 'unixepoch', 'localtime') as starttime,starttime_epoch, datetime(stoptime_epoch, 'unixepoch', 'localtime') as stoptime,stoptime_epoch,responsetime,user,status,iteration,vuser,cache,extra from transactions;")
        c.execute("CREATE VIEW IF NOT EXISTS _faulty_transactions as select * from alltransactions where responsetime = -1;")
        # create view for calculating responsetime	
        c.execute("CREATE VIEW IF NOT EXISTS _calculatedresponsetime as select *, printf('%.3f', [stoptime_epoch] - [starttime_epoch])  as responsetimecalc from alltransactions;")
        # create summary view with calculated responsetimes for using with LR 12.55 with TruClient Chromium - this version is not reporting response times in Javascript
        c.execute("CREATE VIEW IF NOT EXISTS _summarycalculated as select name,percentile(responsetimecalc, 95) as percentile95, avg(responsetimecalc) as avg , max(responsetimecalc) as max , min(responsetimecalc) as min, count(responsetimecalc) as count from _calculatedresponsetime where type='transaction'  and responsetime > -1  group by name order by avg desc;")
        c.execute("CREATE VIEW IF NOT EXISTS passed_failed_actions as select name,   count(case     when responsetime = -1 then 'Failed'    else null    end    )as Failed,  count(case     when responsetime > -1 then 'Passed'    else null    end    )as Passed from alltransactions where type='action' group by name;")
        c.execute("CREATE VIEW IF NOT EXISTS passed_failed_transactions as select name,   count(case     when responsetime = -1 then 'Failed'    else null    end    )as Failed,  count(case when responsetime > -1 then 'Passed'    else null    end    )as Passed from alltransactions where type='transaction' group by name;")
        c.execute("CREATE VIEW IF NOT EXISTS responsetime_of_actions AS select name, vuser, responsetime from alltransactions where  type ='action' group by vuser, name order by vuser, starttime;")
        c.execute("CREATE VIEW IF NOT EXISTS responsetime_of_vuser as select vuser, sum(responsetime) as responsetime from alltransactions where type = 'transaction' group by vuser;")
        c.execute("CREATE VIEW IF NOT EXISTS testduration as select datetime(min(starttime_epoch), 'unixepoch', 'localtime') as starttimetest, datetime(max(stoptime_epoch), 'unixepoch', 'localtime') as stoptimetest, max(stoptime_epoch) - min(starttime_epoch) as duration_seconds, (max(stoptime_epoch) - min(starttime_epoch)) / 60 as duration_minutes from alltransactions;")

        c.execute("CREATE VIEW IF NOT EXISTS _summary_cache AS select name,extra,case cache when 1 then \"cached\" else \"1stvisit\" end as cache ,percentile(responsetime, 90) as percentile90, avg(responsetime) as avg , max(responsetime) as max , min(responsetime) as min, count(responsetime) as count from alltransactions where type='transaction'  and responsetime > -1  group by name,extra,cache order by name,extra,cache desc;")

        c.execute("CREATE INDEX IF NOT EXISTS UpdateQueryLRLogs ON transactions(name, user, vuser, iteration, stoptime_epoch)")

        # insert all the transactions into the database
        for transaction in self:            
            #print ("SQLite: %s" % (transaction.SqLite()))
            c.execute(transaction.SqLite())
            
        # Save (commit) the changes
        conn.commit()

        conn.close()

        return

    def Send2Influx(self, dbhost, dbport, dbname, batchsize, dropdatabase):
        # send all the transaction to an influx database
        print("Send2Influx: %s:%s/%s" % (dbhost, dbport, dbname))
        
        # connect to influx
        client = InfluxDBClient(host=dbhost, port=dbport)
        
        if (dropdatabase):
            # delete the database if required
            client.drop_database(dbname)
    
        # create a new database and switch to the database
        client.create_database(dbname)
        client.switch_database(dbname)

        datapoints = []

        for transaction in self:            
            # walk through all transaction and insert batches into InfluxDb
            datapoints.append(transaction.InfluxDbLine())

            

            if len(datapoints) % batchsize == 0:
                print('Inserting %d datapoints...'%(len(datapoints)))
                
                response = client.write_points(datapoints,  protocol ="line")    

                if response == False:
                    print('Problem inserting points, exiting...')
                    exit(1)

                print("Wrote %d, response: %s" % (len(datapoints), response))

                datapoints = []         

        # check if everything is inserted, else do it now
        if len(datapoints) > 0:
            print('Inserting last %d datapoints...'%(len(datapoints)))
            response = client.write_points(datapoints,  protocol ="line")

            if response == False:
                print('Problem inserting points, exiting...')
                exit(1)

            print("Wrote %d, response: %s" % (len(datapoints), response))


            datapoints = []  

        return

    def SqLite(self):
        # return SQL insert statement for the current transaction
        return "INSERT INTO Transactions(name, type, starttime_epoch, stoptime_epoch, responsetime, user, iteration, cache, status, vuser, extra) VALUES ('%s', '%s', %.3f, %.3f,  %.3f, '%s', %d, %d, '%s', %d, '%s');" % (self.trans, self.type, self.starttime_epoch / 1000000000, self.stoptime_epoch /1000000000 , self.resptime, self.user, self.iteration, self.cache, self.status, self.vuser, self.extra)

    def CSV(self, header):
        # return CSV values for current transaction
        if (header == 1):
            return "name,type,starttime_epoch,stoptime_epoch,responsetime,user,iteration,status,vuser,extra\n"
        else:
            # name, type, starttime_epoch, stoptime_epoch, responsetime, user, iteration, status, vuser, extra
            return "%s,%s,%.3f,%.3f,%.3f,%s,%d,%d,%s,%d,%s\n" % (self.trans, self.type, self.starttime_epoch / 1000000000, self.stoptime_epoch / 1000000000 , self.resptime, self.user, self.iteration, self.cache, self.status, self.vuser, self.extra)
    
    def STT(self, header):
        # return STTX values for current transaction
        if (header == 1):
            return "# header not used in this file format\n#2019-10-04	13:45:00	14:05:00		ExtraAnalyse	1	OK\n"
        else:
            # epoch \t starttime epoch \t stoptime epoch \t responsetime \t transactionname \t num of transactions \t status (OK or ) \t ???? \n
            #return "%s,%s,%.3f,%.3f,%.3f,%s,%d,%d,%s,%d,%s\n" % (self.trans, self.type, self.starttime_epoch / 1000000000, self.stoptime_epoch / 1000000000 , self.resptime, self.user, self.iteration, self.cache, self.status, self.vuser, self.extra)
            if self.resptime > -1:
                return "epoch\t%d\t%d\t\t%s\t%d\t%s\t\n" % (self.starttime_epoch / 1000000, self.stoptime_epoch / 1000000, self.trans, 1, "OK")
            else:
                return ""

    def InfluxDbLine(self):
        # return the InfluxDb Line statement for the current transaction        

        datapoint = "%s" % (self.trans)

        if self.vuser:
            datapoint += ",vuser=%d" % (self.vuser)
        if self.type:
            datapoint += ",type=%s" % (self.type)
        if self.user:
            datapoint += ",user=%s" % (self.user)
        if self.status:
            datapoint += ",status=%s" % (self.status)
        if self.iteration:
            datapoint += ",iteration=%d" % (self.iteration)
        #if self.cache:
        datapoint += ",cache=%d" % (self.cache)

        datapoint += " resptime=%.6f" % (self.resptime)
        datapoint += " %d" % (self.starttime_epoch)
        
        #return "%s,vuser=%s,type=%s,user=%s,status=%s,iteration=%d resptime=%.6f %d\n" %(self.trans, self.vuser, self.type, self.user, self.status, self.iteration, self.resptime,  self.starttime_epoch )


        return datapoint
        

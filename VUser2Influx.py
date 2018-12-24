# used example at https://stackoverflow.com/questions/3428532/how-to-import-a-csv-file-using-python-with-headers-intact-where-first-column-is

import re
import time
import datetime
import argparse
import operator # use for sorting arrays
import os
import sys
from pytz import timezone
from influxdb import InfluxDBClient
from datetime import timedelta
import transactions as transclass




# parse the arguments
parser = argparse.ArgumentParser()

parser.add_argument('--filename', help='VUser logfile to process - wildcard possible', required=True)
parser.add_argument('--csv', help='CSV file to write output to')
parser.add_argument('--sqlite', help='SQLite file to write output to')
parser.add_argument('--dbhost', default="localhost", help='InfluxDb hostname or ip')
parser.add_argument('--dbport', default="8086", help='InfluxDb port number')
parser.add_argument('--dbname', help='InfluxDb database name')
parser.add_argument('--dbdrop', default=0, help='Drop database if exist to ensure a clean database')
parser.add_argument('--batchsize', default=20000, help='How many inserts into InfluxDb in one chunk')
parser.add_argument('--verbose', default=0, help='Display all parameters used in the script')

args = parser.parse_args()

# Show arguments if verbose
if (args.verbose):    
    print("Filename=%s" %(args.filename))
    print("Batchsize=%d" %(args.batchsize))
    print("Dbhost=%s" %(args.dbhost))
    print("Dbport=%s" %(args.dbport))
    print("Dbname=%s" %(args.dbname))
    print("Dbdrop=%d" %(args.dbdrop))
    print("JSON=%d" %(args.json))

# 
#datapoints = []
transactions = []


# open file and read content in to memory - automatically selects what the type of file is
transactions.extend(transclass.transactiontype.ImportLogs(transactions,args.filename))
#transactions.extend(transclass.transactiontype.VUserLog(args.filename))
#transactions.extend(transclass.transactiontype.TruwebLog(args.filename))

# little status update
print ("Found %d transactions " % (len(transactions)))

if (args.dbname):
    # export to Ifflux
    transclass.transactiontype.Send2Influx(transactions, args.dbhost, args.dbport, args.dbname, args.batchsize, args.dbdrop)

if (args.sqlite):
    # export to SQLite
    transclass.transactiontype.Send2SQLite(transactions, args.sqlite, dropdatabase = args.dbdrop)

if (args.csv):
    # export to CSV
    transclass.transactiontype.Send2CSV(transactions, args.csv)
                   




# Import tool for performance testing logs
This tool can help you with importing performance testing logs into several database for futher analysis.

## Import formats
The following formats are available for importing. New ones will follow up on request and/or when needed.

- VUser logs, basically key+value 
- Truweb SQLite DB
- Tikker (http://www.1202performance.com/tools/tikker-the-performance-engineers-stopwatch/)
- JMeter JTL logfiles
    
## Export formats
Output can be send to the following systems:

- InfluxDb
- CSV
- SQLite3

## Commandline reference
```
usage: VUser2Influx.py [-h] --filename FILENAME [--csv CSV] [--sqlite SQLITE]
                       [--dbhost DBHOST] [--dbport DBPORT] [--dbname DBNAME]
                       [--dbdrop DBDROP] [--batchsize BATCHSIZE]
                       [--verbose VERBOSE]
```
                       
- -h Shows the help
- --filename The filenames to import, wildcard supported
- --csv output the data read from the files to a CSV file
- --sqlite output the data read from the files to a SQLite database
- --dbhost Hostname of the Influx database
- --dbport Port of the Influx database
- --dbname The Influx database name
- --dbdrop Drop/clear the database before writing data into it (works with SQLite and Influx)
- --batchsize How many records to drop into the Influx database at once - default: 20000
- --verbose Extra information during processing

## Commandline examples
```
python VUser2Influx.py --filename resultfile_100_vusers.jtl --sqlite test.db3 --dbdrop 1
```

Imports the file resultfile_100_vusers.jtl into test.db3 and drop the database before importing


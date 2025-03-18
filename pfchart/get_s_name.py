import sys,csv
import psycopg2

symbol=sys.argv[1]

def read_file():
  global symbol
  s_names="/var/tmp/history/s_names"
  s_name_list=[]
  symbol=sys.argv[1]
  efile=open(s_names)
  eReader=csv.reader(efile,delimiter=',')
  for row in eReader:
    if row[0] <> "code" and row[0] == symbol:
      print row[1]
      break
  efile.close()

def read_postgres():
  global symbol
  hostname = 'localhost'
  username = 'wls'
  password = 'wholelifestocks'
  database = 'fzdb'

  conn = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
  # Simple routine to run a query on a database and print the results:
  cur = conn.cursor()
  sql = "SELECT symbol, name FROM symbol_list where symbol like '"+symbol+"' or name like '"+symbol+"'"
  cur.execute( sql )

  for firstname, lastname in cur.fetchall() :
    print firstname, lastname

  conn.close()

read_postgres()

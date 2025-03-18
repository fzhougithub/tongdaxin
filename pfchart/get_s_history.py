import os, sys
import tushare as a
import pandas as pd
from sqlalchemy import create_engine
import psycopg2;
from pathlib import Path
import datetime as datetime

stock_symbol=sys.argv[1]
#start=sys.argv[2]

#print(stock_symbol)

def get_to_file(stock_symbol):
  filename="/var/tmp/history/" + stock_symbol
  myfile=Path(filename)
  b=a.get_k_data(stock_symbol,start)
  if b is None:
    if myfile.exists():
      os.remove(filename)
      print >> sys.stderr, stock_symbol," has no data"
      sys.exit(1)	
  outfile = open(filename,'wr')
  b.to_csv(outfile)
  outfile.close()

def get_to_db(stock_symbol):
  hostname='localhost'; username='wls'; password='wholelifestocks'; database='fzdb'
  conn=psycopg2.connect(host=hostname,user=username,password=password,dbname=database)
  cur = conn.cursor()
  sql="select s_history_finalday('"+stock_symbol+"')"
  cur.execute(sql)
  for r in cur.fetchall():
    start=str(r[0]) 
  #print('Get DB start:'+start)
  if start == '1990-01-01':
    b=a.get_k_data(stock_symbol)
  else:
    b=a.get_k_data(stock_symbol,start)
  engine = create_engine('postgresql://wls:wholelifestocks@localhost:5432/fzdb')
  if b is None:
    print("No data for :"+stock_symbol)
  else:
    b.to_sql('tmp_s_history',engine,if_exists='replace')
    sql="INSERT INTO s_history SELECT '"+stock_symbol+"',to_date(date,'yyyy-mm-dd'),open,close,high,low,volume from tmp_s_history ON CONFLICT (symbol,tdate) DO nothing"
    cur.execute(sql)
    conn.commit()
    cur.close()

get_to_db(stock_symbol)

exit(0)




import os, sys
import tushare as ts
import pandas as pd
from sqlalchemy import create_engine
import psycopg2;
from pathlib import Path
import datetime as datetime

stock_symbol=''

def sync_to_file(stock_symbol):
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

def sync_to_db():
  global conn,cur,ts
  ts.set_token('b10be1d6e65cd91419c6a1d4dacf33c955bf60da72bdad6b5009deb9')
  pro = ts.pro_api()
  engine = create_engine('postgresql://wls:wholelifestocks@localhost:5432/fzdb')
  sql="select allign_data()"
  cur.execute(sql)
  for r in cur.fetchall():
    missingdate=str(r[0])
    print missingdate
    df = pro.daily(trade_date=missingdate) 
    if df.empty:
      print("No data for :"+missingdate)
    else:
      df.to_sql('tmp_s_history_missing',engine,if_exists='replace')
      sql="select add_s_history()"
      cur.execute(sql)
      conn.commit()
      for n in cur.fetchone():
        print n;

#===MainCode=====
hostname='localhost'; username='wls'; password='wholelifestocks'; database='fzdb'
conn=psycopg2.connect(host=hostname,user=username,password=password,dbname=database)
cur = conn.cursor()

sync_to_db()

exit(0)

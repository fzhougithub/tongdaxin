import tushare as ts
from sqlalchemy import create_engine
import psycopg2;

hostname='localhost'; username='wls'; password='wholelifestocks'; database='fzdb'
b=ts.get_stock_basics()
engine = create_engine('postgresql://wls:wholelifestocks@localhost:5432/fzdb')
b.to_sql('s_basic',engine,if_exists='replace')
conn=psycopg2.connect(host=hostname,user=username,password=password,dbname=database)
cur = conn.cursor()
sql="insert into symbol_list(symbol,name) select code,name from s_basic on conflict do nothing"
cur.execute(sql)
conn.commit()
cur.close()

exit(0)

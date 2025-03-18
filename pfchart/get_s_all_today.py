import tushare as ts
from sqlalchemy import create_engine

hostname='localhost'; username='wls'; password='wholelifestocks'; database='fzdb'
conn=psycopg2.connect(host=hostname,user=username,password=password,dbname=database)

a = ts.get_today_all()
engine = create_engine('postgresql://wls:wholelifestocks@localhost:5432/fzdb')
a.to_sql('tmp_today',engine,if_exists='replace')
cur = conn.cursor()
sql="INSERT INTO s_history SELECT code,current_date,open,settlement,high,low,volume from tmp_today ON CONFLICT (symbol,tdate) DO nothing"
cur.execute(sql)
conn.commit()
cur.close()

exit(0)

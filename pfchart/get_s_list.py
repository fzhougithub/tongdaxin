import os,sys 
import tushare as ts
import pandas as pd
from pathlib import Path

filename="/var/tmp/history/s_list" 
namefile="/var/tmp/history/s_names"

myfile=Path(filename)

b=ts.get_stock_basics()
if b is None:
	if myfile.exists():
		os.remove(filename)
	print >> sys.stderr, "stock list has no data"
	sys.exit(1)	
outfile = open(filename,'wr')
b.to_csv(outfile)
outfile.close()

os.system("get_s_names")

exit(0)




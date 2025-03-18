import os 
import sys
import tushare as a
import pandas as pd
from pathlib import Path
stock_symbol=sys.argv[1]
print(stock_symbol)
myfile=Path("/Users/frank.zhou/work/wholelifestocks/tmp_hist_data_all.csv")
b=a.get_hist_data(stock_symbol)
if b is None:
	if myfile.exists():
		os.remove('/Users/frank.zhou/work/wholelifestocks/tmp_hist_data_all.csv')
	print >> sys.stderr, stock_symbol," has no data"
	sys.exit(1)	
outfile = open('/Users/frank.zhou/work/wholelifestocks/tmp_hist_data_all.csv','wr')
b.to_csv(outfile)
outfile.close()
exit(0)




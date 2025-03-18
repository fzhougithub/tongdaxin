import sys
import tushare as a
import pandas as pd
stock_symbol=sys.argv[1]
today=sys.argv[2]
print(stock_symbol,today)
#b=a.get_hist_data(stock_symbol,start=today,end=today);
b=a.get_hist_data(stock_symbol);
b.to_csv('/Users/frank.zhou/work/wholelifestocks/tmp_hist_data_all.csv')




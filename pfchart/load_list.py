import sys
import tushare as a
import pandas as pd
b=a.get_stock_basics()
b.to_csv('/Users/frank.zhou/work/wholelifestocks/stock_list.csv')
exit(0)




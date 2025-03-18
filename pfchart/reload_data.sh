#!/bin/bash

export PATH=$PATH:/usr/sbin

TODAY=$(date +%Y-%m-%d)
CODEPATH=/Users/frank.zhou/work/wholelifestocks
LOADLIST=$CODEPATH/load_list.py
#LOADDATA=$CODEPATH/daily_data.py
LOADDATA=$CODEPATH/load_data.py

PYTHON=/Library/Frameworks/Python.framework/Versions/2.7/bin/python
MYSQLIMPORT=/usr/local/bin/mysqlimport
MYSQL=/usr/local/bin/mysql

CSVPATH=/Users/frank.zhou/work/wholelifestocks
LISTFILE=$CSVPATH/stock_list.csv
SOURCEFILE=$CSVPATH/tmp_hist_data_all.csv
INPUTFILE=$CSVPATH/tmp_hist_data.csv

#$PYTHON $LOADLIST
#$MYSQLIMPORT --ignore-lines=1 --fields-terminated-by=, --local -uroot stock $LISTFILE

#stock_list=$($MYSQL -sNe "select symbol from stock.stock_list")
stock_list=$($MYSQL -sNe "select symbol from stock.stock_list where symbol not in (select symbol from stock.hist_data where day='$1')")

for stock_name in $stock_list
do
	$PYTHON $LOADDATA $stock_name 
	if [ -f $SOURCEFILE ];then
		cat $SOURCEFILE |head -5 > $INPUTFILE
		$MYSQLIMPORT --ignore-lines=1 --fields-terminated-by=, --local -uroot stock $INPUTFILE
		sqlstat="use stock;insert ignore hist_data select '"$stock_name"',t.* from tmp_hist_data t;truncate tmp_hist_data"
		#sqlstat="use stock;insert ignore hist_data select '"$stock_name"',t.* from tmp_hist_data t"
		#echo $sqlstat
		$MYSQL -sNe "$sqlstat"
		echo --------------------
	fi
done


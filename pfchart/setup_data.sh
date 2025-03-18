#!/bin/bash

PYCODE=/Users/frank.zhou/work/wholelifestocks/load_data.py
PYTHON=/Library/Frameworks/Python.framework/Versions/2.7/bin/python
MYSQLIMPORT=/usr/local/bin/mysqlimport
SOURCEFILE=/Users/frank.zhou/work/wholelifestocks/tmp_all_hist_data.csv
INPUTFILE=/Users/frank.zhou/work/wholelifestocks/tmp_hist_data.csv

stock_list=$(mysql -sNe "select symbol from stock.stock_list")

for stock_name in $stock_list
do
	$PYTHON $PYCODE $stock_name
	#cat $SOURCEFILE |head -5 > $INPUTFILE
	mv $SOURCEFILE $INPUTFILE
	$MYSQLIMPORT --ignore-lines=1 --fields-terminated-by=, --local -uroot stock $INPUTFILE
	sqlstat="use stock;insert ignore hist_data select '"$stock_name"',t.* from tmp_hist_data t;truncate tmp_hist_data"
	echo $sqlstat
	mysql -sNe "$sqlstat"
done
	


#!/bin/bash

if [ $# -lt 1 ];then
	echo $0 "<stock_symbol> [step]"
	echo example: $0 300393 1
	echo example: $0 300393 
	exit 1
fi

symbol=$1

if [ -z $2 ];then
  step=0
else
  step=$2
fi

datadir=/var/tmp/history
xofile=/var/tmp/history/${symbol}pf.csv
chartfile=/var/tmp/history/${symbol}_chart.py

if [ $(find /var/tmp/history -mtime -1|grep $symbol|wc -l) -eq 0  ];then
	python get_s_history.py $symbol 
	#echo Download Data
fi

python pf_pr_history.py $symbol
#python pf_t1_history.py $symbol $step 
#python pf_s_history.py $symbol $step > $xofile
#python pf_meta.py $symbol

#cat $chartfile

#python $chartfile

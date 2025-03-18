create table tmp_hist_data(
day datetime,
open decimal(11,3),
high decimal(11,3),
close decimal(11,3),
low   decimal(11,3),
volume  decimal(11,3),
price_change decimal(11,3),
p_change  decimal(11,3),
ma5       decimal(11,3),
ma10      decimal(11,3),
ma20      decimal(11,3),
v_ma5     decimal(11,3),
v_ma10    decimal(11,3),
v_ma20    decimal(11,3),
turnover  decimal(11,3)
);

-- get_h_data('002337') qian fu quan

--mv 000001 tmp_hist_data

--mysqlimport --ignore-lines=1 --fields-terminated-by=, --local -uroot stock tmp_hist_data.csv

create table hist_data(
symbol char(6),
day datetime,
open decimal(11,3),
high decimal(11,3),
close decimal(11,3),
low   decimal(11,3),
volume  decimal(11,3),
price_change decimal(11,3),
p_change  decimal(11,3),
ma5       decimal(11,3),
ma10      decimal(11,3),
ma20      decimal(11,3),
v_ma5     decimal(11,3),
v_ma10    decimal(11,3),
v_ma20    decimal(11,3),
turnover  decimal(11,3),
primary key sd(symbol,day)
);

--insert ignore hist_data select '000001',t.* from tmp_hist_data t;

create table stock_list(
symbol char(6),
name   varchar(10),
industry varchar(100),
area   varchar(20),
pe     decimal(6,2),
outstanding  decimal(10,2),
totals   decimal(10,2),
totalAssets  decimal(20,2),
liquidAssets decimal(20,2),
fixedAssets  decimal(20,2),
reserved     decimal(20,2),
reservedPerShare  decimal(10,2),
esp          decimal(6,2),
bvps         decimal(6,2),
pb           decimal(6,2),
timeToMarket datetime,
undp         int,
perundp      decimal(10,2),
rev          decimal(10,2),
profit       decimal(10,2),
gpr          decimal(10,2),
npr          decimal(10,2),
holders      int,
primary key sk(symbol)
);

-- d=a.get_stock_basics();

--mysqlimport --ignore-lines=1 --fields-terminated-by=, --local -uroot stock stock_list.csv

create view hist_sum(symbol,yearmonth,total_v,avg_p) as select symbol,date_format(day,'%Y-%m'),sum(volume),avg(close) from hist_data group by 1,2;


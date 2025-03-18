select date_format(day,'%Y-%m-%d'),sum(volume),avg(close) from hist_data where symbol='002626' group by 1;
select symbol,avg(turnover) from hist_data where day > date_sub(now(),interval 5 day) group by symbol having avg(turnover)>5 order by 2;


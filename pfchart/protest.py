import tushare as ts;
ts.set_token('b10be1d6e65cd91419c6a1d4dacf33c955bf60da72bdad6b5009deb9')
pro = ts.pro_api()
df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
df


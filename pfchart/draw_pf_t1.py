#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import datetime
import psycopg2
import math,datetime
import numpy as np
import numpy,csv,os,sys,subprocess
import tushare as a
import pandas as pd
import pandas as pd1
import matplotlib;
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from matplotlib import rc
from pathlib import Path
#reload(sys)
#sys.setdefaultencoding('utf-8')

#https://stackoverflow.com/questions/5423381/checking-if-sys-argvx-is-defined
symbol=sys.argv[1]
#step=float(sys.argv[2])

step=0
trend=0
v=h=l=o=c=totalV=pH=pL=tpL=tpH=0
bar_x_high=[]
bar_x_bot=[]
bar_o_high=[]
bar_o_bot=[]
bar_x_total=[]
bar_o_total=[]
rx=[]
ro=[]
days=[]
aset=[]
filename="/var/tmp/history/" + symbol
stock_symbol=s_name=''

def ensure_unicode(v):
    if isinstance(v, str):
        v = v.decode('utf8')
    return unicode(v)  # convert anything not a string to unicode too

def draw_pf(topy):
  global trend,trend_status,pH,pL,totalV,l,h,c,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro,days,turnpoint,s_name
  barWidth=1

  dfx = pd.DataFrame({'x':rx,'x_bot':bar_x_bot,'x_high':bar_x_high,'x_v':bar_x_total})
  dfo = pd.DataFrame({'o':ro,'o_bot':bar_o_bot,'o_high':bar_o_high,'o_v':bar_o_total})

  totalx=len(rx)+len(ro)
  plt.figure(figsize=(8,8))
  gs=gridspec.GridSpec(2,1,height_ratios=[5,1])
  fig,axes = plt.subplots(nrows=2,ncols=1,sharex=True,sharey=False)

  axes[0]=plt.subplot(gs[0])
  axes[1]=plt.subplot(gs[1])

  if rx[0] == 2:
    axes[0].bar( 'x','x_high',bottom='x_bot',data=dfx,color='green',width=barWidth)
    axes[0].bar( 'o','o_high',bottom='o_bot',data=dfo,color='red',width=barWidth)
    axes[1].bar( 'x','x_v',data=dfx,color='black',width=barWidth)
    axes[1].bar( 'o','o_v',data=dfo,color='red',width=barWidth)
  elif rx[0] == 1:
    axes[0].bar( 'o','o_high',bottom='o_bot',data=dfo,color='red',width=barWidth)
    axes[0].bar( 'x','x_high',bottom='x_bot',data=dfx,color='green',width=barWidth)
    axes[1].bar( 'o','o_v',data=dfo,color='red',width=barWidth)
    axes[1].bar( 'x','x_v',data=dfx,color='black',width=barWidth)

  ysize=axes[0].get_ylim()
  ymin=ysize[0]
  ymax=ysize[1]
  #print ymin,ymax
  yline=0
  xline=0.5
  ylines=[0]
  xlines=[0]
  totalx=len(rx)+len(ro)
  county=totalx
  g=math.modf(round((ymax-ymin)/county,2)/step)
  if g[1]>0:
    gy=g[1]*step
  else:
    gy=step
  while (yline < ymax):
    yline=yline+gy
    #print yline
    if yline > ymin:
      ylines.append(yline)
  while (xline < totalx):
    xline=xline+1
    xlines.append(xline)

  axes[0].set_yticks(ylines,minor=True)
  axes[0].yaxis.set_label_position("right")
  axes[0].set_xticks(xlines,minor=True)
  axes[1].set_xticks(xlines,minor=True)
  axes[0].yaxis.grid(True, which='minor')
  #axes[0].yaxis.ticker_right()
  axes[0].xaxis.grid(True, which='minor')
  axes[1].xaxis.grid(True, which='minor')

  space=(ymax-ymin)*0.1
  axes[0].set_ybound(ymin-space,ymax)

#https://jdhao.github.io/2017/05/13/guide-on-how-to-use-chinese-with-matplotlib/
#>>> import matplotlib
#>>> matplotlib.matplotlib_fname()
#'/usr/lib64/python2.7/site-packages/matplotlib/mpl-data/matplotlibrc'
#https://www.jianshu.com/p/7b7a3e73ef21

  mpl.rcParams['font.sans-serif'] = ['Heiti SC']
  #mpl.rcParams['font.sans-serif'] = ['Noto Sans SC']
  mpl.rcParams['axes.unicode_minus']=False # in case minus sign is shown as box

  
  #s_name=subprocess.check_output("python get_s_name.py "+stock_symbol+"|cut -d' ' -f2",shell=True)
  s_name=u''.join(ensure_unicode(s_name))
  print(s_name)
  print(stock_symbol)

  #s=u'中粮生化'
  #axes[0].text(0.1,0.2,s_name.format(s),fontproperties=myfont)
  #axes[0].text(0.1,0.2,s_name.format(s))

  axes[0].title.set_text('PF Chart '+ stock_symbol+'|'+s_name+'  ('+days[0]+'~'+days[-1]+') step='+str(step)+' grid='+str(gy))
  axes[1].title.set_text('Volume')

  axes[0].annotate('c/t:'+str(c)+'/'+str(turnpoint), (len(ro)+len(rx), c), xytext=(0.97, (c-ymin+space)/(ymax-ymin+space)), textcoords='axes fraction', arrowprops=dict(arrowstyle="->"))
#  axes[0].annotate('t:'+str(turnpoint), (len(ro)+len(rx), turnpoint), xytext=(0.97, (turnpoint-ymin+space)/(ymax-ymin+space)), textcoords='axes fraction', arrowprops=dict(arrowstyle="->"))
  xsize=axes[0].get_xlim()
  xmax=xsize[1]
  axes[0].axhline(y=c,xmin=(totalx-0.25)/xmax,xmax=(totalx+0.5)/xmax,color='black')
  axes[0].axhline(y=turnpoint,xmin=(totalx-0.25)/xmax,xmax=(totalx+0.5)/xmax,color='blue')

#  axes[0].text(len(ro)+len(rx), turnpoint, turnpoint,va='center', ha="right", bbox=dict(facecolor="yellow",alpha=0.5), transform=axes[0].get_yaxis_transform())
  #axes[0].text(len(ro)+len(rx), turnpoint, str(turnpoint),fontsize='xx-small', va='center', ha="right", bbox=dict(facecolor="yellow",alpha=0.5), transform=axes[0].get_yaxis_transform())

  #axes[0].text(len(ro)+len(rx), (turnpoint-ymin+space)/(ymax-ymin+space), str(turnpoint),fontsize='xx-small', va='center', ha="right", bbox=dict(facecolor="yellow",alpha=0.5), transform=axes[0].get_yaxis_transform())
  #print turnpoint
  a=datetime.datetime.now()
  save_file='/var/tmp/history/'+stock_symbol+'_'+str(a.year)+str(a.month) +str(a.day)
#  print save_file
#  fig.savefig(save_file)

  #print c
  #print rx[0],bar_x_bot[0],bar_x_high[0]
  plt.show()

def load_bars_t1(source_type):
  global trend,trend_status,pH,pL,totalV,l,h,c,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro,days,turnpoint,stock_symbol,s_name

  vflag=''
  vseq=vbase=vadd=vvolume=min_price=max_price=max_total_bar=0
  if source_type=='postgresql':
      hostname='localhost'; username='wls'; password='wholelifestocks'; database='fzdb'
      conn=psycopg2.connect(host=hostname,user=username,password=password,dbname=database)
      cur = conn.cursor()
      cur = conn.cursor()
      sql = "SELECT symbol, name FROM symbol_list where symbol like '"+symbol+"' or name like '"+symbol+"'"
      cur.execute( sql )
      for firstname, lastname in cur.fetchall() :
         stock_symbol=firstname
         s_name=lastname
      sql="select step from pf_bars_info where symbol='"+stock_symbol+"'"
      cur.execute(sql)
      conn.commit()
      if cur.rowcount == 0:
        print("There is no pf bars calculated")
        exit(200)
      for p in cur.fetchone():
        step=float(p)
      sql="select seq,flag,cast(low as float),cast(high as float),cast(volume as float) from pf_bars_t1 where symbol='"+stock_symbol+"' order by seq"
      cur.execute (sql)
      for vseq,vflag,vbase,vadd,vvolume in cur:
        #print vseq,vflag,vbase,vadd,vvolume
        if vflag == 'x':
          rx.append(vseq+1)
          bar_x_bot.append(vbase)
          bar_x_high.append(vadd)
          bar_x_total.append(vvolume)
          trend=1    
          turnpoint=vbase+vadd-4*step
        elif vflag == 'o':
          ro.append(vseq+1)
          bar_o_bot.append(vbase)
          bar_o_high.append(vadd)
          bar_o_total.append(vvolume)
          trend=-1
          turnpoint=vbase+4*step
      max_total_bar=cur.rowcount
      sql="select c from s_history_finalday where symbol='"+stock_symbol+"'"
      cur.execute(sql)
      conn.commit()
      for p in cur.fetchone():
        c=float(p)
      cur.close()
      if max_total_bar == 0:
        print("There is no pre-calculated data in database")
        # fz: Here, the logic should be provided, can recalculate and draw picture, should not be simple just exit
        exit(200)
      sql="select cast(min(low) as float),cast(max(low+high) as float) from pf_bars_t1 where symbol='"+stock_symbol+"'"  
      cur=conn.cursor()
      cur.execute(sql)
      for min_price,max_price in cur.fetchall():
        continue
  trend_status='k'      
  #c=turnpoint
  tpH=(vbase+vadd)-4*step
  tpL=vbase+4*step
  #print rx[0],ro[0]
  #print rx[0],bar_x_bot[0],bar_x_high[0]
  #print ro[0],bar_o_bot[0],bar_o_high[0]
  return step, max_total_bar,max_price 

#==== Main ===========================
if stock_symbol is None:
  print("Must input correct stock symbol")
  exit(100)
  

p_set=load_bars_t1("postgresql")
#TODO: 1. Date need to be added into the bar, but, how to organize the original calculation fomular is headache
#TODO: 2. Turnpoint, phL and plH how to keep track? or just based on the following data?  
#=====================
days.append('2016-01-01')
now = datetime.datetime.now()
days.append(now.strftime("%Y-%m-%d"))
#=====================


#print p_set[0],p_set[1],p_set[2],step
#print len(rx),len(bar_x_bot),len(bar_x_high),len(bar_x_total) 
#print len(ro),len(bar_o_bot),len(bar_o_high),len(bar_o_total)
#print rx,bar_x_bot,bar_x_high,bar_x_total
#print ro,bar_o_bot,bar_o_high,bar_o_total
#print p_set
if p_set[2] >0:
  draw_pf(p_set[2])
else:
  print("No Result")
  
exit(0)


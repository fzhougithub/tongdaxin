#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import math,datetime
import numpy as np
import numpy,csv,os,sys,subprocess
import tushare as a
import pandas as pd
import matplotlib;
#matplotlib.use('macosx')
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from matplotlib import rc
from pathlib import Path
#reload(sys)
#sys.setdefaultencoding('utf-8')

#https://stackoverflow.com/questions/5423381/checking-if-sys-argvx-is-defined
stock_symbol=sys.argv[1]
step=float(sys.argv[2])

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

def ensure_unicode(v):
    if isinstance(v, str):
        v = v.decode('utf8')
    return unicode(v)  # convert anything not a string to unicode too

def bar_append(bar_type):
   global pH,pL,totalV,rx,ro,bar_x_high,bar_x_bot,bar_o_high,bar_o_bot 
   if bar_type == 'x':
     if len(rx) == len(bar_x_high):
       rx.append(rx[-1]+2)
     bar_x_high.append(pH-pL)
     bar_x_bot.append(pL)
     bar_x_total.append(totalV)
   elif bar_type == 'o':
     if len(ro) == len(bar_o_high):
       ro.append(ro[-1]+2)
     bar_o_high.append(pH-pL)
     bar_o_bot.append(pL)
     bar_o_total.append(totalV)

def bar_remove(bar_type):
   global pH,pL,totalV,rx,ro,bar_x_high,bar_x_bot,bar_o_high,bar_o_bot
   if bar_type == 'x':
     p=len(bar_x_bot)-1
     del bar_x_bot[p]
     del bar_x_high[p]
     del bar_x_total[p]
     del rx[p]
   elif bar_type == 'o':
     p=len(bar_o_bot)-1
     del bar_o_bot[p]
     del bar_o_high[p]
     del bar_o_total[p]
     del ro[p]

def mod_up(x,unit):
  n=0
  if x>unit:
	rmod=math.modf(x/unit)
	if rmod[0]>unit/2:
	  n=rmod[1]+1
	else:
	  n=rmod[1]
	return n*unit

def mod_down(x,unit):
  n=0
  if x>unit:
        rmod=math.modf(x/unit)
        if rmod[0]>unit/2:
          n=rmod[1]+1
	else:
	  n=rmod[1]
        return n*unit
  else:
        return x
	
#def bar_error_check():
#  global trend,pH,pL,totalV,l,h,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro
#  if rx[-1]>ro[-1] and len(bar_x_bot)>0 and len(bar_o_bot)>0:
#     if bar_x_bot[-1]-bar_o_bot[-1]-step <>0:
#       print('Error1: rx='+str(rx[-1])+' ro='+str(ro[-1]))
#  elif rx[-1]<ro[-1] and len(bar_x_bot)>0 and len(bar_o_bot)>0:
#     if bar_x_bot[-1]+bar_x_high[-1]-step <> bar_o_bot[-1]+bar_o_high[-1]:
#       print('Error2: rx='+str(rx[-1])+' ro='+str(ro[-1])+' rx_high='+str(bar_x_bot[-1]+bar_x_high[-1])+' ro_high='+str(bar_o_bot[-1]+bar_o_high[-1]))

def trend_keep():
  global trend,pH,h,pL,l,totalV,tpH,tpL,step,v
  if trend == 1: 
    if pH < mod_up(h,step):
       pH=mod_up(h,step)
    tpH=pH-step*4
    if pL == 0:
      pL = mod_down(l,step)
  elif trend == -1:
    if pL>mod_down(l,step):
       pL=mod_down(l,step)
    tpL=pL+step*4
    if pH == 0:
      pH = mod_up(h,step)
  totalV=totalV+v
#  print("trend_keep:"+str(trend)+"|"+str(totalV)+"|"+str(pH)+'|'+str(pL)+'|'+str(pH)+'|'+str(pL))
#  print('trend_keep:h('+str(h)+')l('+str(l)+')pH('+str(pH)+')tpH('+str(tpH)+')tpL('+str(tpL)+')pL('+str(pL)+')totalV('+str(totalV)+')trend('+str(trend)+')')


def trend_turn():
  global trend,pH,pL,totalV,l,h,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro
  #print('trent:'+str(trend))
  if (trend == 1):
    trend=-1
    if mod_up(h,step)>pH:
       pH=mod_up(h,step)
    bar_append('x')
#    print("UpStop:bar_x_added:pL="+str(bar_x_bot[-1])+",pH="+str(bar_x_bot[-1]+bar_x_high[-1])+",rx="+str(rx[-1]))
#    bar_error_check()
#    print("X: pH="+str(pH)+",pL="+str(pL)+",v="+str(totalV)) 
    pH=pH-step
    tpH=pH-step*4
    if tpH-step > mod_down(l,step):
      pL=mod_down(l,step)
    else:
        pL=tpH-step
    tpL=pL+step*4
    totalV=v
  elif (trend == -1):
    trend=1
    #print('changed from -1 to 1:'+str(trend))
     #print("O,"+str(pH-pL)+","+str(pL)+","+str(totalV))
    bar_append('o')
#    print("DownStop:bar_o_added:pH="+str(bar_o_bot[-1]+bar_o_high[-1])+",pL="+str(bar_o_bot[-1])+",ro="+str(ro[-1]))
#    bar_error_check()
    pL=pL+step
    tpL=pL+step*4
    if tpL+step < mod_up(h,step):
      pH=mod_up(h,step)
    else:
      pH=tpL+step
    tpH=pH-step*4
    totalV=v
#  print('NewTrend('+str(trend)+') after set rx='+str(rx[-1])+'|ro='+str(ro[-1])+':h('+str(h)+')l('+str(l)+')pH('+str(pH)+')tpH('+str(tpH)+')tpL('+str(tpL)+')pL('+str(pL)+')totalV('+str(totalV))

def trend_unknown():
  global trend,pH,pL,totalV,c,l,h,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro
  if pH == pL and pH == 0:
    pH=mod_up(h,step)
    tpH=pH-4*step
    pL=mod_down(l,step)
    tpL=pL+4*step
  elif mod_down(l,step)<pL:
    pL=mod_down(l,step)
    tpL=pL+4*step
  elif mod_up(h,step)>pH:
    pH=mod_up(h,step)
    tpH=pH-4*step
    totalV=totalV+v
  if pH-pL > 5*step:
    if l>tpH and c > tpH:
      trend=1
      rx.append(1)
      ro.append(2)
      trend_status='k'
    elif h<tpL and c < tpL:
      trend=-1
      rx.append(2)
      ro.append(1)
      trend_status='k'
  totalV=totalV+v
#  print('trend_unknown:h('+str(h)+')l('+str(l)+')pH('+str(pH)+')pL('+str(pL)+')totalV('+str(totalV)+')trend('+str(trend)+')')

def trend_rollback():
  global trend,trend_status,pH,pL,totalV,l,h,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro
  if trend == 1:
    trend = -1
    trend_status='k'
    pH=bar_o_bot[-1]+bar_o_high[-1]
    tpH=pH-4*step
    pL=bar_o_bot[-1]
    tpL=pL+4*step
    totalV=totalV+bar_o_total[-1]
    bar_remove('o')
#    print("bar_o_removed trend -1 pH="+str(pH)+",pL="+str(pL)+",rx"+str(rx[-1])+"|ro="+str(ro[-1])+'x_bot='+str(bar_x_bot[-1])+'x_high='+str(bar_x_high[-1]))
#    bar_error_check()
    trend_keep()
  elif trend == -1:
    trend = 1
    trend_status='k'
    pH=bar_x_bot[-1]+bar_x_high[-1]
    tpH=pH-4*step
    pL=bar_x_bot[-1]
    tpL=pL+4*step
    totalV=totalV+bar_x_total[-1]
    bar_remove('x')
#    print("bar_x_removed trend 1 pL="+str(pL)+",pH="+str(pH)+",rx="+str(rx[-1])+'|ro='+str(ro[-1])+',o_bot'+str(bar_o_bot[-1])+',o_high='+str(bar_o_high[-1]))
#    bar_error_check()
    trend_keep()
#  print('trend_rollback:h('+str(h)+')l('+str(l)+')pH('+str(pH)+')tpH('+str(tpH)+')tpL('+str(tpL)+')pL('+str(pL)+')totalV('+str(totalV)+')trend('+str(trend)+')rx='+str(rx[-1])+'|ro='+str(ro[-1]))


def check_result():
  global trend,trend_status,pH,pL,totalV,l,h,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro
#  for i in range(len(rx)):
     #print('rx='+str(rx[i])+',pL='+str(bar_x_bot[i])+',pH='+str(bar_x_bot[i]+bar_x_high[i]))
#  print len(rx),len(bar_x_bot),len(bar_x_total),len(ro),len(bar_o_bot),len(bar_o_total)


def final_bar():
  global trend,trend_status,pH,pL,totalV,l,h,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro,turnpoint
  if trend_status == 'k':
    if trend == 1:
      bar_append('x')
      turnpoint=tpH
      #print step, bar_x_bot[-1],bar_x_bot[-1]+bar_x_high[-1]
    elif trend == -1:
      bar_append('o')
      turnpoint=tpL
      #print step, bar_o_bot[-1],bar_o_bot[-1]+bar_o_high[-1]
  if trend_status == 't':
    if trend == 1:
      bar_append('x')
      turnpoint=tpH
    elif trend == -1:
      bar_append('o') 
      turnpoint=tpL
  
#print(stock_symbol)
filename="/var/tmp/history/" + stock_symbol
#myfile=Path(filename)
#histbars=numpy.loadtxt(open(filename,"rb"),delimiter=",",skiprows=0)


def prepare_data():
  global step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro,aset,days,stock_symbol
  rr=[]
  best_step=max_price=max_total_bar=0

  if step == 0:
    block=0.01
    n=0
    while (step < 10):
#    while (step < 10 and max_total_bar<100):
      n=n+1
      step=step+block
      #print n, step,max_total_bar,max_price
      try:
          r_set=calculate_dataset()
#	if max_price < r_set[1]:
          max_price=r_set[1]
#        if max_total_bar < r_set[0]:
          max_total_bar=r_set[0]
          best_step=step
          if max_total_bar>50:
             rr.append([best_step,max_total_bar])
        #print n,best_step,max_total_bar,max_price
      except:
        #print("Error: calculate_dataset:step="+str(step)+":"+str(best_step)+",max_total_bar="+str(max_total_bar))
        pass
    if len(rr)>0:
      max_total_bar=100
      for countr,v_rr in enumerate(rr):
         b=v_rr[1]
     #    print v_rr[0],v_rr[1]
         if max_total_bar>=v_rr[1]:
            max_total_bar=v_rr[1]
            best_step=v_rr[0] 
      step=best_step
      #print step,max_total_bar
      r_set=calculate_dataset()
      max_total_bar=r_set[0]
      max_price=r_set[1]
      return best_step,max_total_bar,max_price
    else:
      print("Manually Check /var/tmp/history/"+stock_symbol)
      return step,0,0
  else:
    r_set=calculate_dataset()
    max_total_bar=r_set[0]
    max_price=r_set[1]
    return step,max_total_bar,max_price

def calculate_dataset():
  global trend,trend_status,pH,pL,totalV,l,h,c,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro,aset,days

  trend=0
  v=h=l=o=c=totalV=pH=pL=tpL=tpH=y=0
  maxy=0
  bar_x_high=[]
  bar_x_bot=[]
  bar_o_high=[]
  bar_o_bot=[]
  bar_x_total=[]
  bar_o_total=[]
  rx=[]
  ro=[]
  days=[]

  trend_status='k'

  for counter,row in enumerate(aset):
    if (counter>1):
      days.append(row[1])
      h=float(row[4])
      c=float(row[3])
      l=float(row[5])
      v=float(row[6])
      #print('eReader:'+str(eReader.line_num)+'|'+str(h)+'|'+str(l)+'|'+str(c)+'|'+str(v))
      if (trend == 0 or pH-pL<4*step ):
        trend_unknown()
        trend_status='u'
      if ((c >= tpH and trend == 1) or ( c <= tpL and trend == -1)):
	trend_keep()
	trend_status='k'
      elif ((c <tpH and trend == 1) or ( c > tpL and trend == -1)):
        if trend_status =='k':
	  trend_turn()
          trend_status='t' 
        elif trend_status =='t' and len(rx) > 3 and len(ro) > 3:
	  trend_rollback()
	  trend_status='k'
  final_bar()
  total_bars=len(ro)+len(rx)
  if total_bars>1:
    yxl=[]
    ybl=[]
    for xb,xh in zip(bar_x_bot,bar_x_high):
      yxl.append(xb+xh)
    for ob,oh in zip(bar_o_bot,bar_o_high):
      ybl.append(ob+oh)
    maxy=max(max(yxl),max(ybl))
  #print total_bars,maxy
  return total_bars,maxy

def draw_pf(topy):
  global trend,trend_status,pH,pL,totalV,l,h,c,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro,days,turnpoint
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
  mpl.rcParams['axes.unicode_minus']=False # in case minus sign is shown as box

  
  s_name=subprocess.check_output('python get_s_name.py '+stock_symbol,shell=True)
  s_name=u''.join(ensure_unicode(s_name))
  print s_name

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
#  fig.savefig(save_file,dpi=gcf().dpi)
  fig.savefig(save_file,dpi=fig.dpi)

  #print c
  #print rx[0],bar_x_bot[0],bar_x_high[0]
#  plt.show()


#==== Main ===========================
if stock_symbol is None:
  print("Must input correct stock symbol")
  exit(100)
  
efile=open(filename)
eReader=csv.reader(efile,delimiter=',')
for row in eReader:
  aset.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]])
efile.close()

p_set=prepare_data()
#print p_set[0],step
if p_set[2] >0:
  draw_pf(p_set[2])
else:
  print("No Result")

exit(0)


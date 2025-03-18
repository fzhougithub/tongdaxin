import numpy as np
import numpy,csv,os,sys 
import tushare as a
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from pathlib import Path
stock_symbol=sys.argv[1]
step=float(sys.argv[2])
trend=1
v=h=l=o=c=totalV=pH=pL=tpL=tpH=0
bar_x_high=bar_x_bot=bar_o_high=bar_o_bot=bar_x_total=bar_o_total=[]
rx=[1]
ro=[2]

def trend_keep():
  global trend,pH,h,pL,l,totalV,tpH,tpL,step,v
  if trend == 1: 
    if pH < h:
       pH=h
       tpH=pH-step*3
       if pL == 0:
          pL = l
  if trend == -1:
    if l<pL:
       pL=l
       tpL=pL+step*3
       if pH == 0:
          pH = h
  totalV=totalV+v
#  print("trend_keep:"+str(trend)+"|"+str(totalV)+"|"+str(pH)+'|'+str(pL)+'|'+str(pH)+'|'+str(pL))


def trend_turn():
  global trend,pH,pL,totalV,l,h,tpH,tpL,v,step,bar_x_high,bar_o_high,bar_x_bot,bar_o_bot,bar_x_total,bar_o_total,rx,ro
  if trend == 1:
     trend=-1
     print("X,"+str(pH-pL)+","+str(pL)+","+str(totalV))
     bar_x_high.append(str(pH-pL)
     bar_x_bot.append(str(pL)
     bar_x_total.append(str(totalV))
     rx.append(rx[-1]+2)
#     print("X: pH="+str(pH)+",pL="+str(pL)+",v="+str(totalV)) 
     totalV=v
     pH=pH-step
     pL=l
     tpL=pL+step*3
  if trend == -1:
     trend=1
     print("O,"+str(pH-pL)+","+str(pL)+","+str(totalV))
     bar_o_high.append(str(pH-pL)
     bar_o_bot.append(str(pL)
     bar_o_total.append(str(totalV))
     ro.append(ro[-1]+2)
#     print("O: pH="+str(pH)+",pL="+str(pL)+",v="+str(totalV))
     pL=pL+step
     pH=h
     tpH=pH-step*3

#print(stock_symbol)
filename="/var/tmp/history/" + stock_symbol
#myfile=Path(filename)
#histbars=numpy.loadtxt(open(filename,"rb"),delimiter=",",skiprows=0)

efile=open(filename)
eReader=csv.reader(efile,delimiter=',')

for row in eReader:
  if (row[2] != 'high'):
    h=float(row[2])
    c=float(row[3])
    l=float(row[4])
    v=float(row[5])
    if ((c > tpH and trend == 1) or ( c < tpL and trend == -1)):
	trend_keep()
    elif ((c < tpH and trend == 1) or (c > tpL and trend == -1)):
        trend_turn()
  else:
    if row[1] is None:
	break
    continue

if (c > tpH and trend == 1):
     bar_o_high.append(str(pH-pL))
     bar_o_bot.append(str(pL))
     bar_o_total.append(str(totalV))
     ro.append(ro[-1]+2)
#  print("O,"+str(pH-pL)+","+str(pL)+","+str(totalV))
if ( c < tpL and trend == -1):
#  print("X,"+str(pH-pL)+","+str(pL)+","+str(totalV))
     bar_x_high.append(str(pH-pL))
     bar_x_bot.append(str(pL))
     bar_x_total.append(str(totalV))
     rx.append(rx[-1]+2)

efile.close()

print("Completed List Creation")
barWidth=0.5

print ("bar_x_high:"+bar_x_high)
print bar_x_bot
print rx
print ro

plt.bar(rx,bar_x_high,bottom=bar_x_bot,color='green',width=barWidth)
plt.bar(ro,bar_o_high,bottom=bar_o_bot,color='blue',width=barWidth)
plt.show()

#exit(0)




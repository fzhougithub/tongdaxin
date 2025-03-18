import numpy
import csv,os 
import sys
import tushare as a
import pandas as pd
from pathlib import Path
stock_symbol=sys.argv[1]
step=float(sys.argv[2])
trend=1
v=h=l=o=c=totalV=pH=pL=tpL=tpH=0

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
  global trend,pH,pL,totalV,l,h,tpH,tpL,v,step
  if trend == 1:
     trend=-1
     print("X,"+str(pH-pL)+","+str(pL)+","+str(totalV))
#     print("X: pH="+str(pH)+",pL="+str(pL)+",v="+str(totalV)) 
     totalV=v
     pH=pH-step
     pL=l
     tpL=pL+step*3
  if trend == -1:
     trend=1
     print("O,"+str(pH-pL)+","+str(pL)+","+str(totalV))
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
  if (row[1] != 'date'):
    h=float(row[4])
    c=float(row[3])
    l=float(row[5])
    v=float(row[6])
    if ((c > tpH and trend == 1) or ( c < tpL and trend == -1)):
	trend_keep()
    elif ((c < tpH and trend == 1) or (c > tpL and trend == -1)):
        trend_turn()
  else:
    if row[1] is None:
	break
    continue

if (c > tpH and trend == 1):
  print("O,"+str(pH-pL)+","+str(pL)+","+str(totalV))
if ( c < tpL and trend == -1):
  print("X,"+str(pH-pL)+","+str(pL)+","+str(totalV))
  
    

efile.close()

exit(0)




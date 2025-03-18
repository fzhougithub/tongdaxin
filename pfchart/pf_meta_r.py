# libraries
import csv,os,sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
 
stock_symbol=sys.argv[1]
filename="/var/tmp/history/" + stock_symbol + "pf.csv"
efile=open(filename)
eReader=csv.reader(efile,delimiter=',')
rx=ro=top_X=top_O=bot_X=bot_O=']'

for row in eReader:
  if row[0] == 'X':
    top_X=',' + row[1]+top_X
    bot_X=',' + row[2]+bot_X
    rx=rx+str(eReader.line_num)+','
  if row[0] == 'O':
    top_O=top_O+row[1]+','
    bot_O=bot_O+row[2]+','
    ro=ro+str(eReader.line_num)+','

top_X=top_X[:-1]+']'
bot_X=bot_X[:-1]+']'
top_O=top_O[:-1]+']'
bot_O=bot_O[:-1]+']'
rx=rx[:-1]+']'
ro=ro[:-1]+']'

#print ("bar_x_high = "+top_X)
#print ("bar_x_bot = "+bot_X)
#print ("bar_o_high = "+top_O)
#print ("bar_o_bot = "+bot_O)	
#print ("rx = "+rx)
#print ("ro = "+ro)

chartfile='/var/tmp/history'+stock_symbol+'_chart.py'
if os.path.exists(chartfile):
  os.remove(chartfile)
else:
  f=open("/var/tmp/history/"+stock_symbol+"_chart.py","w")
  f.write("import csv,os,sys\n")
  f.write("import numpy as np\n")
  f.write("import matplotlib.pyplot as plt\n")
  f.write("from matplotlib import rc\n")
  f.write("import pandas as pd\n")
  f.write("bar_x_high = "+top_X+'\n')
  f.write("bar_x_bot = "+bot_X+'\n')
  f.write("bar_o_high = "+top_O+'\n')
  f.write("bar_o_bot = "+bot_O+'\n')
  f.write("rx = "+rx+'\n')
  f.write("ro = "+ro+'\n')
  f.write("barWidth=0.5\n")
  f.write("plt.bar(rx,bar_x_high,bottom=bar_x_bot,color='green',width=barWidth)\n")
  f.write("plt.bar(ro,bar_o_high,bottom=bar_o_bot,color='blue',width=barWidth)\n")
  f.write("plt.show()\n")

# y-axis in bold
rc('font', weight='bold')
 
# Values of each group
bars1 = [12, 28, 1, 8, 22]
bars2 = [28, 7, 16, 4, 10]
bars3 = [25, 3, 23, 25, 17]
 
# Heights of bars1 + bars2 (TO DO better)
bars = [40, 35, 17, 12, 32]
 
# The position of the bars on the x-axis
r = [0,1,2,3,4]
 
# Names of group and bar width
#names = ['A','B','C','D','E']
barWidth = 1
 
rx= [0,2,4,6,8,10]
ro= [1,3,5,7,9,11]

# Create brown bars
#plt.bar(r, bars1, color='white', edgecolor='white', width=barWidth)
#plt.bar(r, bars1, color='#7f6d5f', edgecolor='white', width=barWidth)
# Create green bars (middle), on top of the firs ones
#plt.bar(r, bars2, bottom=bars1, color='white', edgecolor='white', width=barWidth)
#plt.bar(r, bars2, bottom=bars1, color='#557f2d', edgecolor='white', width=barWidth)
# Create green bars (top)
#plt.bar(r, bars3, bottom=bars, color='white', edgecolor='white', width=barWidth)
#plt.bar(r, bars3, bottom=bars, color='#2d7f5e', edgecolor='white', width=barWidth)
 
# Custom X axis
#plt.xticks(r, names, fontweight='bold')
#
#plt.xlabel("group")
 
# Show graphic
#plt.show()


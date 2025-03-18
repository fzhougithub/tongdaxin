# libraries
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.gridspec as gridspec


df1=pd.DataFrame({'x': [1,2,3,4,5],  'y': [3,2,9,30,17], 'z': [12,100,48,75,21], 'b1':[1,0,7,12,10] })


#df1=pd.DataFrame({'x': range(1,101), 'y': np.random.randn(100)*15+range(1,101), 'z': (np.random.randn(100)*41+range(1,101))*10 })
 
# initialise the figure. here we share X and Y axis

plt.figure(figsize=(16,8))
gs = gridspec.GridSpec(2, 1, height_ratios=[6, 1])
fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, sharey=False)

axes[0]=plt.subplot(gs[0])
axes[1]=plt.subplot(gs[1])
axes[0].bar( 'x','y',bottom='b1',data=df1)
axes[1].bar( 'x','z', data=df1)
axes[0].title.set_text('These 2 plots have the same limit for the X axis')
plt.show()


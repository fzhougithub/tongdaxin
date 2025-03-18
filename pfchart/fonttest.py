#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import sys,subprocess
import matplotlib as mpl
import matplotlib.pyplot as plt
font_name = "Songti SC Light"

def ensure_unicode(v):
    if isinstance(v, str):
        v = v.decode('utf8')
    return unicode(v)  # convert anything not a string to unicode too

stock_symbol=sys.argv[1]
s_name=subprocess.check_output('python get_s_name.py '+stock_symbol,shell=True)
s_name=u''.join(ensure_unicode(s_name))
#s_name='测试'
s=u'测'
print s.encode('utf-8')
print u'测试'.encode('utf-8')
print s_name

mpl.rcParams['font.sans-serif'] = ['Heiti SC']
mpl.rcParams['axes.unicode_minus']=False # in case minus sign is shown as box

plt.text(0.5, 0.5, s=u'测试')
#plt.text(0.1, 0.1, s=str(s_name).format(s))
plt.text(0.1, 0.1, s=s_name)
#plt.text(0.1, 0.1, s=s_name%s)
plt.show()

#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt
import sys

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

font_path='/System/Library/Fonts/'
prop = mfm.FontProperties(fname=font_path)

plt.text(0.5, 0.5, s=u'测试', fontproperties=prop)
plt.show()


# coding: utf-8

# In[2]:


# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *

import MySQLdb
import codecs
from datetime import *
import time
import sys
sys.path.append('../')
from DB import *
from StockManager import *
from IndexManager import *
from FundamentalsManager import *

set_token('a0998908534d317105b2184afbe436a4104dc51b')

fieldstr = 'DY,EV,EVEBITDA,EVPS,LYDY,NEGOTIABLEMV,PB,PCLFY,PCTTM,PELFY,PELFYNPAAEI,PEMRQ,PEMRQNPAAEI,PETTM,PETTMNPAAEI,PSLFY,PSMRQ,PSTTM,TCLOSE,TOTMKTCAP,TRADEDATE,TURNRATE,TOTAL_SHARE,FLOW_SHARE'
table = 'trading_derivative_indicator'
providor = FundamentalsManager()
stockManager = StockManager()

for code in stockManager.getStockList():
    print("##", code, "##")
    fundamentals = providor.getFundamentals(code, table, fieldstr)
    providor.saveFundamentals(code, fundamentals, table, fieldstr)
    time.sleep(0.1)



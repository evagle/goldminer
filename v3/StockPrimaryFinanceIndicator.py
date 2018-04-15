
# coding: utf-8

# In[ ]:


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

fieldstr = 'EBIT,EBITDA,EBITDASCOVER,EBITSCOVER,EPSBASIC,EPSBASICEPSCUT,EPSDILUTED,EPSDILUTEDCUT,EPSFULLDILUTED,EPSFULLDILUTEDCUT,EPSWEIGHTED,EPSWEIGHTEDCUT,NPCUT,OPNCFPS,ROEDILUTED,ROEDILUTEDCUT,ROEWEIGHTED,ROEWEIGHTEDCUT'
table = 'prim_finance_indicator'
providor = FundamentalsManager()
stockManager = StockManager()

for code in stockManager.getStockList():
    print("##", code, "##")
    fundamentals = providor.getFundamentals(code, table, fieldstr)
    providor.saveFundamentals(code, fundamentals, table, fieldstr)
    time.sleep(0.1)


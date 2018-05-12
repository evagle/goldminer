
# coding: utf-8

# In[ ]:


# coding=utf-8
from __future__ import absolute_import, print_function, unicode_literals

import sys

from gm.api import *

sys.path.append('../')
from storage.DB import *
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


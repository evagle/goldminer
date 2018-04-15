
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

set_token('a0998908534d317105b2184afbe436a4104dc51b')


# class FundamentalsData():
#     def __init__(self):
#         self.db = DB()

#     def getSymbol(self, code):
#         if code[0:1] == "6":
#             return "SHSE"
#         return "SZSE"

#     def getFundamentals(self, code):
#         startdate = self.db.getLastFundamentalsDate(code)
#         enddate = datetime.now()+timedelta(days=1)
#         print(startdate, enddate, self.getSymbol(code)+ "." +code)
#         results = get_fundamentals(table='trading_derivative_indicator', symbols=self.getSymbol(code) + "." + code, 
#             start_date=startdate, end_date=enddate, 
#                 fields='DY,EV,EVEBITDA,EVPS,LYDY,NEGOTIABLEMV,PB,PCLFY,PCTTM,PELFY,PELFYNPAAEI,PEMRQ,PEMRQNPAAEI,PETTM,PETTMNPAAEI,PSLFY,PSMRQ,PSTTM,TCLOSE,TOTMKTCAP,TRADEDATE,TURNRATE,TOTAL_SHARE,FLOW_SHARE')
#         return results

#     def saveFundamentals(self, code, fundamentals):
# #         for fundamental in fundamentals:
#         if len(fundamentals) > 0:
#             self.db.addFundamental(code, fundamentals)
#             print("insert %d fundamentals" % len(fundamentals))
#         else:
#             print("%s is up to date" % code)

            
fieldstr = 'DY,EV,EVEBITDA,EVPS,LYDY,NEGOTIABLEMV,PB,PCLFY,PCTTM,PELFY,PELFYNPAAEI,PEMRQ,PEMRQNPAAEI,PETTM,PETTMNPAAEI,PSLFY,PSMRQ,PSTTM,TCLOSE,TOTMKTCAP,TRADEDATE,TURNRATE,TOTAL_SHARE,FLOW_SHARE'
table = 'trading_derivative_indicator'
providor = FundamentalsManager()
stockManager = StockManager()
for code in stockManager.getStockList():
    print("##", code, "##")
    fundamentals = providor.getFundamentals(code, table, fieldstr)
    providor.saveFundamentals(code, fundamentals, table, fieldstr)

    
# providor = FundamentalsData()
# stockManager = StockManager()
# for code in stockManager.getStockList():
#     print("##", code, "##")
#     fundamentals = providor.getFundamentals(code)
#     providor.saveFundamentals(code, fundamentals)
    # break


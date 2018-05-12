
# coding: utf-8

# In[ ]:


from __future__ import absolute_import, print_function, unicode_literals

import sys

sys.path.append('../')
from storage.DB import *

class StockService:
    def __init__(self):
        self.db = DB()
        self.stockPETTMCache = {}

    def _dateToStr(self, date):
        return date.strftime("%Y-%m-%d")
    
    def _loadStockPETTM(self, stockCode):
        if stockCode in self.stockPETTMCache:
            return
        sql = "SELECT end_date, PETTM FROM trading_derivative_indicator WHERE code = '%s'"
        sql = sql % stockCode
        result = self.db.executeSql(sql)
        pe = {}
        for row in result:
            pe[self._dateToStr(row[0])] = row[1]
        self.stockPETTMCache[stockCode] = pe
        print("Load stock %s PETTM successfully" % stockCode)
        
    def getStockPETTM(self, stockCode, date):
        if stockCode not in self.stockPETTMCache:
            self._loadStockPETTM(stockCode)
        return self.stockPETTMCache[stockCode][self._dateToStr(date)]



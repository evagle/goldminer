
# coding: utf-8

# In[4]:


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

set_token('a0998908534d317105b2184afbe436a4104dc51b')

class StockData():
    def __init__(self):
        self.db = DB()
        
    def getStockList(self):
        return self.db.getStockList()
    
    def getSymbol(self, code):
        if code[0:1] == "6":
            return "SHSE"
        return "SZSE"
    
    def queryAllStockBar(self, md, code):
        startdate = self.db.getStockLatestDate(code)
        if startdate is None:
            startdate = self.db.getStockStartDate(code)
        else:
            startdate = startdate + timedelta(days=1)
        enddate = datetime.now()+timedelta(days=1)
        print(startdate, enddate)
        bars = md.get_dailybars(self.getSymbol(code) + "." + code, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
        return bars
    
    def saveBars(self, bars):
        for bar in bars:
            self.db.addStockDailyBar(bar)
        print("insert %d bars" % len(bars))

class IndexData():
    def __init__(self):
        self.db = DB()
        
    def getIndexList(self):
        return self.db.getIndexList()
    
    def getSymbol(self, code):
        if code[0:1] == "0":
            return "SHSE"
        return "SZSE"
    
    def queryInstituents(self, code):
        startdate = self.db.getLastIndexDate(code)
        enddate = datetime.now()+timedelta(days=1)
        print(startdate, enddate, self.getSymbol(code)+ "." +code)
        results = get_history_constituents(index=self.getSymbol(code)+ "." +code, start_date=startdate, end_date=enddate)
        return results
    
    def saveConstituents(self, code, constituents):
        for constituent in constituents:
            self.db.addIndexConstituent(code, constituent)
        print("insert %d constituents" % len(constituents)) 
        

indexData = IndexData()
for code in indexData.getIndexList():
    print("##", code, "##")
    results = indexData.queryInstituents(code)
    indexData.saveConstituents(code, results)
    time.sleep(1)
# data = get_history_constituents(index='SHSE.000001',start_date='2017-12-31', end_date='2017-12-31')
# print(data)


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

class StockManager():
    def __init__(self):
        self.db = DB()
        
    def getStockList(self):
        return self.db.getStockList()
    
    def getSymbol(self, code):
        if code[0:1] == "6" or code[0:1] == "9":
            return "SHSE"
        return "SZSE"
    
    # def queryAllStockBar(self, md, code):
    #     startdate = self.db.getStockLatestDate(code)
    #     enddate = datetime.now() + timedelta(days=1)
    #     print(startdate, enddate)
    #     bars = md.get_dailybars(self.getSymbol(code) + "." + code, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
    #     return bars
    
    # def saveBars(self, bars):
    #     count = 0
    #     for bar in bars:
    #         count += self.db.addStockDailyBar(bar)
    #     print("Total %s bars, successfully insert %d bars" % (len(bars), count))


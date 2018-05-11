# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *

import sys
sys.path.append('../')
from storage.DB import *

set_token('a0998908534d317105b2184afbe436a4104dc51b')

class IndexManager():
    def __init__(self):
        self.db = DB()
        
    def getIndexList(self):
        return self.db.getIndexList()
    
    def getSymbol(self, code):
        if code[0:1] == "0":
            return "SHSE"
        return "SZSE"
    
    def queryInstituents(self, code):
        startdate = self.db.getLastIndexConstituentsDate(code) + timedelta(days=1)
        enddate = datetime.now()+timedelta(days=1)
        print("start=",startdate, "end=", enddate, "code=", self.getSymbol(code)+ "." +code)
        results = get_history_constituents(index=self.getSymbol(code)+ "." +code, start_date=startdate, end_date=enddate)
        print("results len = ", len(results))
        return results
    
    def saveConstituents(self, code, constituents):
        count = 0
        for constituent in constituents:
            count += self.db.addIndexConstituent(code, constituent)
        print("Total %d constituents, successfully insert %s constituents" % (len(constituents), count))
    
    def queryAllBars(self, code):
        startdate = self.db.getIndexBarLatestDate(code)
        enddate = datetime.now() + timedelta(days=1)
        print(startdate, enddate, self.getSymbol(code) + "." + code)
        symbol = self.getSymbol(code) + "." + code
        bars = history(symbol, "1d", startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
        return bars
    
    def saveBars(self, bars):
        count = self.db.addIndexDailyBar(bars)
        print("Total %d index bars, successfully insert %d bars" % (len(bars), count))
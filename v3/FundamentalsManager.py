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

class FundamentalsManager():
    def __init__(self):
        self.db = DB()

    def getSymbol(self, code):
        if code[0:1] == "6" or code[0:1] == "9":
            return "SHSE"
        return "SZSE"

    def getFundamentals(self, code, table, fieldstr):
        startdate = self.db.getLastFundamentalsDate(code, table)
        enddate = datetime.now()+timedelta(days=1)
        print(startdate, enddate, self.getSymbol(code)+ "." +code)
        results = get_fundamentals(table=table, symbols=self.getSymbol(code) + "." + code, 
            start_date=startdate, end_date=enddate, limit=10000,
                fields=fieldstr)
        return results

    def removeDuplicate(self, fundamentals):
        results = {}
        for fundamental in fundamentals:
            key = fundamental['symbol'] + fundamental['pub_date'].strftime("%Y-%m-%d") + fundamental['end_date'].strftime("%Y-%m-%d")
            if key in results and not self.isSame(fundamental, results[key]):
                print("*****", fundamental, results[key])
            else:
                results[key] = fundamental
        return results.values()
    
    def isSame(self, item1, item2):
        keys = item1.keys()
        for key in keys:
            if key not in item2 or item1[key] != item2[key]:
                return False
        return True
    def saveFundamentals(self, code, fundamentals, table, fieldstr):
#         for fundamental in fundamentals:
        # fundamentals = self.removeDuplicate(fundamentals)
        count = 0
        if len(fundamentals) > 0:
            count = self.db.addFundamental(code, fundamentals, table, fieldstr)
            print("Total %s items, successfully insert %d into %s" % (len(fundamentals), count, table))
        else:
            print("%s is up to date" % code)


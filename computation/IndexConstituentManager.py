
# coding: utf-8

# In[73]:

from __future__ import print_function, absolute_import, unicode_literals

import MySQLdb
import codecs
from datetime import *
import time
import pandas as pd

import sys
sys.path.append('../')
from DB import *
import json

class IndexConstituentManager:
    def __init__(self):
        self.db = DB()
        
    def _getWeights(self, code, date):
#         print(nextMonth, date)
        # 如果能找到一条记录的trade_date >= date,则找到时间最早的一条记录
        # trade_date=2018-01-31这条记录代表了2018-01-01~2018-01-31的weight
        sql = "SELECT code, trade_date, constituents, no_weight from index_constituents WHERE code = '%s' and trade_date >= '%s' ORDER BY trade_date ASC LIMIT 1"
        sql = sql % (code, date.strftime("%Y-%m-%d"))
        result = self.db.executeSql(sql)

        if len(result) > 0 and result[0][3] == 0:
            return result[0]
        
        # 如果没有记录比date早，说明现在的权重还没出来，继续用之前一个月的权重
        # 超过一个月还是没有新记录则是出错了
        sql = "SELECT code, trade_date, constituents from index_constituents WHERE code = '%s' and trade_date < '%s' and no_weight = 0 ORDER BY trade_date DESC LIMIT 1"
        sql = sql % (code, date.strftime("%Y-%m-%d"))
        result = self.db.executeSql(sql)
        if len(result) > 0 and result[0][1] + timedelta(days=92) > date.date():
            return result[0]
        return None
    
    def getWeights(self, code, date):
        result = self._getWeights(code, date)
        if result is None:
            return None
        
        data = json.loads(result[2])
        weights = {}
        for k in data:
            weights[k[5:]] = data[l]
        print(weights)
        return weights
    
    # 获取指数成份股，如果能获取到weights则直接返回
    # 否则尝试获取constituents
    # trade_date >= query_date && trade_date 最小
    def _getConstituents(self, code, date):
        result = self._getWeights(code, date)
        if result is not None:
            data = list(json.loads(result[2]).keys())
            constituents = []
            for c in data:
                constituents.append(c[5:])
            return [result[0], result[1], constituents]
        
        sql = "SELECT code, trade_date, constituents from index_constituents WHERE code = '%s' and trade_date >= '%s' and no_weight = 1 ORDER BY trade_date ASC LIMIT 1"
        sql = sql % (code, date.strftime("%Y-%m-%d"))
        result = self.db.executeSql(sql)
        if len(result) == 0:
            return None
        
        sql = "SELECT count(*) from index_constituents WHERE code = '%s' and trade_date > '%s' and no_weight = 1 ORDER BY trade_date ASC LIMIT 1"
        sql = sql % (code, date.strftime("%Y-%m-%d"))
        count = self.db.executeSql(sql)
        if len(count) == 0:
            return None
        
        return result[0]
    
    def _getConstituentsForTest(self, code, date):
        result = self._getConstituents(code, date)
        if result is None:
            return None
        return result[1]
    
    def getConstituents(self, code, date):
        result = self._getConstituents(code, date)
        if result is None:
            return None
        if isinstance(result[2], list):
            return result[2]
        data = json.loads(result[2])
        constituents = []
        for c in data:
            constituents.append(c[5:])
        return constituents
    


# In[76]:


class IndexConstituentManagerTest:
    def __init__(self):
        self.instance = IndexConstituentManager()
    
    def testGetConstituents(self):
        d = self.instance._getConstituentsForTest('000001', datetime(1999, 12, 1))
        print("expect None, real =", d)
        assert(d == date(2001, 1, 1))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2001, 1, 1))
        print("expect ",date(2001, 1, 1), " real =", d)
        assert(d == date(2001, 1, 1))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2001, 1, 4))
        print("expect ",date(2001, 1, 5), " real =", d)
        assert(d == date(2001, 1, 5))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2001, 2, 26))
        print("expect ",date(2001, 2, 27), " real =", d)
        assert(d == date(2001, 2, 27))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2009, 8, 28))
        print("expect ",date(2009, 8, 28), " real =", d)
        assert(d == date(2009, 8, 28))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2011, 4, 23))
        print("expect ",date(2011, 5, 13), " real =", d)
        assert(d == date(2011, 5, 13))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2011, 5, 10))
        print("expect ",date(2011, 5, 13), " real =", d)
        assert(d == date(2011, 5, 13))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2011, 5, 20))
        print("expect ",date(2011, 5, 20), " real =", d)
        assert(d == date(2011, 5, 20))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2011, 5, 25))
        print("expect ",date(2011, 5, 31), " real =", d)
        assert(d == date(2011, 5, 31))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2011, 6, 1))
        print("expect ",date(2011, 6, 30), " real =", d)
        assert(d == date(2011, 6, 30))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2018, 3, 20))
        print("expect ",date(2018, 3, 30), " real =", d)
        assert(d == date(2018, 3, 30))
        
        d = self.instance._getConstituentsForTest('000001', datetime(2018, 5, 20))
        print("expect ",date(2018, 3, 30), " real =", d)
        assert(d == date(2018, 3, 30))
        
        
# test = IndexConstituentManagerTest()
# test.testGetConstituents()


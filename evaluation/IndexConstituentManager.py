# coding: utf-8

# In[73]:

from __future__ import absolute_import, print_function, unicode_literals

import sys

from storage.IndexConstituentDao import IndexConstituentDao

sys.path.append('../')
from storage.DB import *
import json


class IndexConstituentManager:
    def __init__(self):
        self.db = DB()
        self.indexConstituentDao = IndexConstituentDao()

    def getWeights(self, code, date):
        result = self.indexConstituentDao.getConstituents(code, date)
        if result is None:
            return None

        data = json.loads(result[2])
        weights = {}
        for k in data:
            weights[k[5:]] = data[k]
        print(weights)
        return weights

    def __formatConstituents(self, data):
        if data[3] == 1:
            constituents = [c[5:] for c in json.loads(data[2])]
            return [data[0], data[1], constituents]
        else:
            keys = list(json.loads(data[2]).keys())
            constituents = [c[5:] for c in keys]
            return [data[0], data[1], constituents]

    # 获取指数成份股，如果能获取到weights则直接返回
    # 否则尝试获取constituents
    # trade_date >= query_date && trade_date 最小
    def _getConstituents(self, code, date):
        result = self.indexConstituentDao.getConstituents(code, date)
        if result is not None:
            return self.__formatConstituents(result)
        return None

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
        print("expect ", date(2001, 1, 1), " real =", d)
        assert (d == date(2001, 1, 1))

        d = self.instance._getConstituentsForTest('000001', datetime(2001, 1, 1))
        print("expect ", date(2001, 1, 1), " real =", d)
        assert (d == date(2001, 1, 1))

        d = self.instance._getConstituentsForTest('000001', datetime(2001, 1, 4))
        print("expect ", date(2001, 1, 5), " real =", d)
        assert (d == date(2001, 1, 5))

        d = self.instance._getConstituentsForTest('000001', datetime(2001, 2, 26))
        print("expect ", date(2001, 2, 27), " real =", d)
        assert (d == date(2001, 2, 27))

        d = self.instance._getConstituentsForTest('000001', datetime(2009, 8, 28))
        print("expect ", date(2009, 8, 28), " real =", d)
        assert (d == date(2009, 8, 28))

        d = self.instance._getConstituentsForTest('000001', datetime(2011, 4, 23))
        print("expect ", date(2011, 5, 13), " real =", d)
        assert (d == date(2011, 5, 13))

        d = self.instance._getConstituentsForTest('000001', datetime(2011, 5, 10))
        print("expect ", date(2011, 5, 13), " real =", d)
        assert (d == date(2011, 5, 13))

        d = self.instance._getConstituentsForTest('000001', datetime(2011, 5, 20))
        print("expect ", date(2011, 5, 20), " real =", d)
        assert (d == date(2011, 5, 20))

        d = self.instance._getConstituentsForTest('000001', datetime(2011, 5, 25))
        print("expect ", date(2011, 5, 31), " real =", d)
        assert (d == date(2011, 5, 31))

        d = self.instance._getConstituentsForTest('000001', datetime(2011, 6, 1))
        print("expect ", date(2011, 6, 30), " real =", d)
        assert (d == date(2011, 6, 30))

        d = self.instance._getConstituentsForTest('000001', datetime(2018, 3, 20))
        print("expect ", date(2018, 3, 30), " real =", d)
        assert (d == date(2018, 3, 30))


test = IndexConstituentManagerTest()
test.testGetConstituents()

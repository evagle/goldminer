# coding: utf-8
import unittest
from datetime import date

from goldminer.indicators.IndexConstituentManager import IndexConstituentManager


class IndexConstituentManagerTest(unittest.TestCase):

    def setUp(self):
        self.instance = IndexConstituentManager()

    def testGetConstituents(self):
        d = self.instance._getConstituentsForTest('000001', date(1999, 12, 1))
        assert (d == date(2001, 1, 1))

        d = self.instance._getConstituentsForTest('000001', date(2001, 1, 1))
        assert (d == date(2001, 1, 1))

        d = self.instance._getConstituentsForTest('000001', date(2001, 1, 4))
        assert (d == date(2001, 1, 5))

        d = self.instance._getConstituentsForTest('000001', date(2001, 2, 26))
        assert (d == date(2001, 2, 27))

        d = self.instance._getConstituentsForTest('000001', date(2009, 8, 28))
        assert (d == date(2009, 8, 28))

        d = self.instance._getConstituentsForTest('000001', date(2011, 4, 23))
        assert (d == date(2011, 5, 13))

        d = self.instance._getConstituentsForTest('000001', date(2011, 5, 10))
        assert (d == date(2011, 5, 13))

        d = self.instance._getConstituentsForTest('000001', date(2011, 5, 20))
        assert (d == date(2011, 5, 20))

        d = self.instance._getConstituentsForTest('000001', date(2011, 5, 25))
        assert (d == date(2011, 5, 31))

        d = self.instance._getConstituentsForTest('000001', date(2011, 6, 1))
        assert (d == date(2011, 6, 30))

        d = self.instance._getConstituentsForTest('000001', date(2018, 3, 20))
        assert (d == date(2018, 3, 30))


if __name__ == '__main__':
    unittest.main()

"""StockDao test"""
import unittest
from datetime import date

from goldminer.storage.StockDailyBarDao import StockDailyBarDao


class StockDailyBarAdjustNoneDaoTest(unittest.TestCase):

    def setUp(self):
        self.dao = StockDailyBarDao()

    def tearDown(self):
        pass

    def testGetLatestDate(self):
        d = self.dao.getLatestDate('000001')
        self.assertLess(date(2018, 5, 8), d)

        d = self.dao.getLatestDate('none')
        self.assertEqual(date(2001, 1, 1), d)


if __name__ == '__main__':
    unittest.main()






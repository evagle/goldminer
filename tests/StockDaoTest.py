"""StockDao test"""
import unittest
from datetime import date

from models.models import Stock
from storage.StockDao import StockDao


class StockDaoTest(unittest.TestCase):

    def setUp(self):
        self.dao = StockDao()

    def tearDown(self):
        pass

    def testGetAll(self):
        result = self.dao.all()
        self.assertTrue(len(result) > 10)
        self.assertEqual(type(result[0]), Stock)

    def testGetStockList(self):
        result = self.dao.getStockList()
        self.assertTrue(len(result) > 10)

    def testGetStockPublishDate(self):
        d = self.dao.getStockPublishDate('000001')
        self.assertEqual(date(1991, 4, 3), d)

        d = self.dao.getStockPublishDate('none')
        self.assertEqual(None, d)

if __name__ == '__main__':
    unittest.main()






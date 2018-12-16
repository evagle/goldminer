import unittest
from datetime import date

from goldminer.models.models import BalanceSheet, TradingDerivativeIndicator, PrimaryFinanceIndicator, IncomeStatement
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao


class StockFundamentalsDaoTest(unittest.TestCase):

    def setUp(self):
        self.dao = StockFundamentalsDao()

    def testGetLatestDateValidCode(self):
        d = self.dao.getLatestDate('000001', BalanceSheet)
        self.assertLess(date(2018, 3, 1), d)

        d = self.dao.getLatestDate('000001', IncomeStatement)
        self.assertLess(date(2018, 3, 1), d)

        d = self.dao.getLatestDate('000001', PrimaryFinanceIndicator)
        self.assertLess(date(2018, 3, 1), d)

        d = self.dao.getLatestDate('000001', TradingDerivativeIndicator)
        self.assertLess(date(2018, 3, 1), d)

        # d = self.dao.getLatestDate('000001', CashflowStatement)
        # self.assertLess(date(2018, 3, 1), d)
        #
        # d = self.dao.getLatestDate('000001', DerivativeFinanceIndicator)
        # self.assertLess(date(2018, 3, 1), d)

    def testGetLatestDateInvalidCode(self):
        d = self.dao.getLatestDate('none', BalanceSheet)
        self.assertEqual(date(2001, 1, 1), d)

        d = self.dao.getLatestDate('none', IncomeStatement)
        self.assertEqual(date(2001, 1, 1), d)

        d = self.dao.getLatestDate('none', PrimaryFinanceIndicator)
        self.assertEqual(date(2001, 1, 1), d)

        d = self.dao.getLatestDate('none', TradingDerivativeIndicator)
        self.assertEqual(date(2001, 1, 1), d)




if __name__ == '__main__':
    unittest.main()






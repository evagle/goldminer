# coding: utf-8
from models.models import TradingDerivativeIndicator, IndexDailyBar
from storage.StockFundamentalsDao import StockFundamentalsDao
from datetime import date


class StockManager:

    def __init__(self):
        self.fundamentalsDao = StockFundamentalsDao()
        self.__stockPETTMCache = {}
        self.__tradeDatesCache = []

        # load trade dates when initiate
        self.__loadTradeDates()
        print(self.__tradeDatesCache)

    def __loadStockPETTM(self, stockCode):
        if stockCode in self.__stockPETTMCache:
            return

        session = self.fundamentalsDao.getSession()
        result = session.query(TradingDerivativeIndicator.end_date, TradingDerivativeIndicator.PETTM) \
            .filter(TradingDerivativeIndicator.code == stockCode)

        pe = {}
        for row in result:
            pe[row[0].strftime("%Y-%m-%d")] = row[1]
        self.__stockPETTMCache[stockCode] = pe
        print("Load stock %s PETTM successfully" % stockCode)

    def getStockPETTM(self, stockCode, d: date):
        if stockCode not in self.__stockPETTMCache:
            self.__loadStockPETTM(stockCode)
        return self.__stockPETTMCache[stockCode][d.strftime("%Y-%m-%d")]

    def __loadTradeDates(self):
        session = self.fundamentalsDao.getSession()
        dates = session.query(IndexDailyBar.trade_date) \
            .filter(IndexDailyBar.code == '000001')
        for d in dates:
            self.__tradeDatesCache.append(d[0])

    def getTradeDates(self):
        return self.__tradeDatesCache

    def isTradeDate(self, d: date):
        return d in self.__tradeDatesCache


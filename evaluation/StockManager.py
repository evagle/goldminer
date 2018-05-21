# coding: utf-8
from models.models import TradingDerivativeIndicator, IndexDailyBar, StockDailyBarAdjustNone
from storage.IndexesDao import IndexesDao
from storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from storage.StockDao import StockDao
from storage.StockFundamentalsDao import StockFundamentalsDao
from datetime import date


class StockManager:

    def __init__(self):
        self.fundamentalsDao = StockFundamentalsDao()
        self.stockDao = StockDao()

        self.__stockPETTMCache = {}
        self.__tradeDatesCache = []

        # load trade dates when initiate
        self.__loadTradeDates()
        self.stockPETTMNotFound = {}

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
        print("[%s] Load %d PETTM successfully" % (stockCode, len(pe)))

    def getStockPETTM(self, stockCode, d: date):
        if stockCode not in self.__stockPETTMCache:
            self.__loadStockPETTM(stockCode)

        datestr = d.strftime("%Y-%m-%d")
        if datestr in self.__stockPETTMCache[stockCode]:
            return self.__stockPETTMCache[stockCode][datestr]
        else:
            if stockCode in self.stockPETTMNotFound:
                self.stockPETTMNotFound[stockCode] += 1
            else:
                self.stockPETTMNotFound[stockCode] = 1
            return 0

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

    def getSuspensionDates(self, code):
        stockBarDao = StockDailyBarAdjustNoneDao()
        tradeDates = stockBarDao.getAllTradeDatesByCode(code)
        candidates = list(set(self.__tradeDatesCache).difference(set(tradeDates)))
        startDate = self.stockDao.getStockPublishDate(code)
        suspensionDates = [d for d in candidates if d >= startDate]
        suspensionDates.sort()
        print("[%s] %d suspension dates" % (code,  len(suspensionDates)))
        return suspensionDates



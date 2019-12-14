# coding: utf-8
import time
from datetime import date, datetime

from goldminer.common.Utils import Utils
from goldminer.models.models import IndexDailyBar, TradingDerivativeIndicator
from goldminer.storage.StockDailyBarDao import StockDailyBarDao
from goldminer.storage.StockDao import StockDao
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao


class StockManager:
    __tradeDatesCache = None
    __tradeDatesDict = None

    def __init__(self):
        self.fundamentalsDao = StockFundamentalsDao()
        self.stockDao = StockDao()

        # load trade dates when initiate
        self.__loadTradeDates()

    def getFieldByName(self, field):
        if field == "PETTM":
            return TradingDerivativeIndicator.PETTM
        elif field == "PB":
            return TradingDerivativeIndicator.PB
        elif field == "TotalMarketValue":
            return TradingDerivativeIndicator.TOTMKTCAP

    def __loadTradeDates(self):
        if StockManager.__tradeDatesCache is not None:
            return
        StockManager.__tradeDatesCache = []
        StockManager.__tradeDatesDict = {}

        session = self.fundamentalsDao.getSession()
        dates = session.query(IndexDailyBar.trade_date) \
            .filter(IndexDailyBar.code == '000001')
        for d in dates:
            StockManager.__tradeDatesCache.append(d[0])
            StockManager.__tradeDatesDict[d[0]] = True
        StockManager.__tradeDatesCache.sort()

    def getTradeDates(self):
        return StockManager.__tradeDatesCache

    def getLastTradeDate(self):
        return StockManager.__tradeDatesCache[-1:]

    def isTradeDate(self, d):
        if type(d) is datetime:
            d = d.date()
        return d in StockManager.__tradeDatesDict

    def getPreviousTradeDate(self, d):
        pos = StockManager.__tradeDatesCache.index(d)
        if pos > 0:
            pos = pos - 1
        else:
            raise Exception("No previous trade date found.")
        return StockManager.__tradeDatesCache[pos]

    def getSuspensionDates(self, code):
        stockBarDao = StockDailyBarDao()
        tradeDates = stockBarDao.getAllTradeDatesByCode(code)
        candidates = list(set(StockManager.__tradeDatesCache).difference(set(tradeDates)))
        startDate = self.stockDao.getStockPublishDate(code)
        suspensionDates = [d for d in candidates if d >= startDate]
        suspensionDates.sort()
        print("[%s] %d suspension dates" % (code, len(suspensionDates)))
        return suspensionDates


if __name__ == "__main__":
    manager = StockManager()
    print(manager.getLastTradeDate())

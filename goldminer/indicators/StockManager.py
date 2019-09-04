# coding: utf-8
import time
from datetime import date, datetime

from goldminer.common.Utils import Utils
from goldminer.models.models import IndexDailyBar, TradingDerivativeIndicator
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDao import StockDao
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao


class StockManager:

    def __init__(self):
        self.fundamentalsDao = StockFundamentalsDao()
        self.stockDao = StockDao()

        '''
        {
            '000001' : 
            {
                "pe" : 
                {
                     "date1" : v1, 
                     ...
                }, 
                "pb" : 
                {
                     "date2" : v2
                     ...      
                }
            }
        }
        '''
        self.__stockCache = {}
        self.__tradeDatesCache = []

        # load trade dates when initiate
        self.__loadTradeDates()

    def getFieldByName(self, field):
        if field == "PETTM":
            return TradingDerivativeIndicator.PETTM
        elif field == "PB":
            return TradingDerivativeIndicator.PB
        elif field == "TotalMarketValue":
            return TradingDerivativeIndicator.TOTMKTCAP

    def __preLoadTradingDerivative(self):
        if len(self.__stockCache) > 0:
            print("Cache for TradingDerivativeIndicator already loaded.")
            return

        start = time.clock()

        session = self.fundamentalsDao.getSession()
        result = session.query(TradingDerivativeIndicator.code,
                               TradingDerivativeIndicator.end_date,
                               TradingDerivativeIndicator.PETTM,
                               TradingDerivativeIndicator.PB,
                               TradingDerivativeIndicator.TOTMKTCAP)
        for row in result:
            # cache[code][trade_date] = {fields}
            code = row[0]
            date = row[1]
            if code not in self.__stockCache:
                self.__stockCache[code] = {}

            self.__stockCache[code][date] = {
                "PETTM": row[2],
                "PB": row[3],
                "TotalMarketValue": row[4],
            }
        end = time.clock()
        print(
            "Load {} TradingDerivativeIndicator PE,PB,TOTMKTCAP successfully, time = {}".format(len(self.__stockCache),
                                                                                                end - start))

    def __loadStockField(self, stockCode, field):
        if stockCode in self.__stockCache and field in self.__stockCache[stockCode]:
            return

        if stockCode not in self.__stockCache:
            self.__stockCache[stockCode] = {}

        session = self.fundamentalsDao.getSession()
        fieldColumn = self.getFieldByName(field)
        result = session.query(TradingDerivativeIndicator.end_date, fieldColumn) \
            .filter(TradingDerivativeIndicator.code == stockCode)

        data = {}
        for row in result:
            data[row[0].strftime("%Y-%m-%d")] = row[1]
        self.__stockCache[stockCode][field] = data
        print("[%s] Load %d %s successfully" % (stockCode, len(data), field))

    def getStockFieldByDate(self, code, field, d: date):
        if code not in self.__stockCache:
            self.__preLoadTradingDerivative()

        if code in self.__stockCache and d in self.__stockCache[code] and field in self.__stockCache[code][d]:
            return self.__stockCache[code][d][field]
        else:
            return 0

    def getStockPETTM(self, stockCode, d: date):
        field = "PETTM"
        return self.getStockFieldByDate(stockCode, field, d)

    def getStockPB(self, stockCode, d: date):
        field = "PB"
        return self.getStockFieldByDate(stockCode, field, d)

    def getStockTotalMarketValue(self, stockCode, d: date):
        field = "TotalMarketValue"
        return self.getStockFieldByDate(stockCode, field, d)

    def __loadTradeDates(self):
        session = self.fundamentalsDao.getSession()
        dates = session.query(IndexDailyBar.trade_date) \
            .filter(IndexDailyBar.code == '000001')
        for d in dates:
            self.__tradeDatesCache.append(d[0])
        self.__tradeDatesCache.sort()

    def getTradeDates(self):
        return self.__tradeDatesCache

    def getLastTradeDate(self):
        return self.__tradeDatesCache[-1:]

    def isTradeDate(self, d: date):
        if type(d) is datetime:
            d = d.date()
        return d in self.__tradeDatesCache

    def getPreviousTradeDate(self, d):
        pos = self.__tradeDatesCache.index(d)
        if pos > 0:
            pos = pos - 1
        else:
            raise Exception("No previous trade date found.")
        return self.__tradeDatesCache[pos]

    def getSuspensionDates(self, code):
        stockBarDao = StockDailyBarAdjustNoneDao()
        tradeDates = stockBarDao.getAllTradeDatesByCode(code)
        candidates = list(set(self.__tradeDatesCache).difference(set(tradeDates)))
        startDate = self.stockDao.getStockPublishDate(code)
        suspensionDates = [d for d in candidates if d >= startDate]
        suspensionDates.sort()
        print("[%s] %d suspension dates" % (code, len(suspensionDates)))
        return suspensionDates


if __name__ == "__main__":
    manager = StockManager()
    print(manager.getLastTradeDate())

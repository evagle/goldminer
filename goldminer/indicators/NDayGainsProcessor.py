# coding: utf-8
import math

from goldminer.indicators.BaseIndicatorProcessor import BaseIndicatorProcessor
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from goldminer.storage.StockDao import StockDao


class NDayGainsProcessor(BaseIndicatorProcessor):
    def __init__(self):
        self.stockBarPrevDao = StockDailyBarAdjustPrevDao()
        self.stockDao = StockDao()

    def process(self, code, **kwargs):
        '''

        :param code:
        :param kwargs:
                    n: int, n days
                    refresh: bool, refresh all data
        :return:
        '''
        n = self.get_args(kwargs, "n", 0)
        refresh = self.get_args(kwargs, "refresh", False)

        if n > 50:
            bars = self.stockBarPrevDao.getN(code, n)
        else:
            bars = self.stockBarPrevDao.getAll(code)

        changedBars = []
        for n in [50, 120, 250]:
            for i in range(n, len(bars)):
                attr = "gain" + str(n)

                # close可能等于零，此时找后面的几个bar
                close = 0
                for j in range(10):
                    close = bars[i - n + j].close
                    if close > 0:
                        break
                    else:
                        print("Error bar close = 0", bars[i - n + j])

                val = (bars[i].close - close) / close * 100 if close > 0 else 0

                oldval = getattr(bars[i], attr)
                if refresh or oldval is None or math.fabs(oldval-val) > 1e-6:
                    setattr(bars[i], attr, val)
                    changedBars.append(bars[i])

        print(len(changedBars), "bars updated")
        self.stockBarPrevDao.bulkSave(changedBars)

    def updateAll(self, nDays = 7):
        stocks = self.stockDao.getStockList()
        processor = NDayGainsProcessor()
        for code in stocks:
            print("start calculate n days gain for", code)
            processor.process(code, n = nDays)
            print("end", code)

if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    processor = NDayGainsProcessor()
    for code in stocks:
        print("start", code)
        processor.process(code)
        print("end", code)
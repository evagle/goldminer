# coding: utf-8
from goldminer.indicators.BaseIndicatorProcessor import BaseIndicatorProcessor
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from goldminer.storage.StockDao import StockDao


class NDayGainsProcessor(BaseIndicatorProcessor):
    def __init__(self):
        self.stockBarPrevDao = StockDailyBarAdjustPrevDao()

    def process(self, code, **kwargs):
        key_ndays = "n"
        if key_ndays in kwargs and kwargs[key_ndays] > 50:
            bars = self.stockBarPrevDao.getN(code, kwargs[key_ndays])
        else:
            bars = self.stockBarPrevDao.getAll(code)

        for n in [50, 120, 250]:
            for i in range(n, len(bars)):
                attr = "gain" + str(n)
                val = (bars[i].close - bars[i - n].close) / bars[i - n].close * 100
                setattr(bars[i], attr, val)
                print(i)
        self.stockBarPrevDao.bulkSave(bars)


if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    processor = NDayGainsProcessor()
    for code in stocks:
        print("start", code)
        processor.process(code)
        print("end", code)

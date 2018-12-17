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

                # close可能等于零，此时找后面的几个bar
                close = 0
                for j in range(10):
                    close = bars[i - n + j].close
                    if close > 0:
                        break
                    else:
                        print("Error bar close = 0", bars[i - n + j])

                val = (bars[i].close - close) / close * 100 if close > 0 else 0
                setattr(bars[i], attr, val)

        self.stockBarPrevDao.bulkSave(bars)


if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    processor = NDayGainsProcessor()
    for code in stocks:
        print("start", code)
        processor.process(code)
        print("end", code)
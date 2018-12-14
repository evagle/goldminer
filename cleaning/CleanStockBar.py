# coding: utf-8
from storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from storage.StockDao import StockDao


class CleanStockBar:
    @staticmethod
    def checkAndTagAbnormalBar(code):
        stockBarDao =  StockDailyBarAdjustPrevDao()
        bars = stockBarDao.getAll(code)
        for i in range(1, len(bars)):
            if (bars[i].close > bars[i - 1].close * 1.2 or bars[i].close < bars[i - 1].close * 0.8) and \
                    (bars[i].close > bars[i + 1].close * 1.2 or bars[i].close < bars[i + 1].close * 0.8):
                bars[i].open = bars[i-1].open
                bars[i].close = bars[i - 1].close
                bars[i].high = bars[i - 1].high
                bars[i].low = bars[i - 1].low
                bars[i].pre_close = bars[i - 1].pre_close
                bars[i].fix_abnormal = "1"
                stockBarDao.add(bars[i])


if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    for code in stocks:
        CleanStockBar.checkAndTagAbnormalBar(code)


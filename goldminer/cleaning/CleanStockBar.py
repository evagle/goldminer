# coding: utf-8
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from goldminer.storage.StockDao import StockDao


class CleanStockBar:
    @staticmethod
    def checkAndTagAbnormalBar(code):
        stockBarDao = StockDailyBarAdjustPrevDao()
        bars = stockBarDao.getAll(code)
        for i in range(2, len(bars)):
            # 1. 明显与前后两根线不符
            cond1 = ((i + 1 < len(bars)) and
                     (bars[i].close > bars[i - 1].close * 1.2 or bars[i].close < bars[i - 1].close * 0.8) and
                     (bars[i].close > bars[i + 1].close * 1.2 or bars[i].close < bars[i + 1].close * 0.8))

            # 2. 明显与前一根线后5根不符
            cond2 = ((i + 5 < len(bars)) and
                     (bars[i].close > bars[i - 1].close * 1.2 or bars[i].close < bars[i - 1].close * 0.8) and
                     (bars[i].close > bars[i + 5].close * 1.2 or bars[i].close < bars[i + 5].close * 0.8))

            if cond1 or cond2:
                bars[i].open = bars[i - 1].open
                bars[i].close = bars[i - 1].close
                bars[i].high = bars[i - 1].high
                bars[i].low = bars[i - 1].low
                bars[i].pre_close = bars[i - 1].pre_close
                bars[i].fix_abnormal = "1"
                stockBarDao.add(bars[i])
                print(bars[i])


if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    for code in stocks:
        CleanStockBar.checkAndTagAbnormalBar(code)


# coding: utf-8
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from goldminer.storage.StockDao import StockDao
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao


class BuyPointInvestigation:
    def __init__(self):
        self.stockBarDao = StockDailyBarAdjustPrevDao()
        self.stockFundamentals = StockFundamentalsDao()




if __name__ == "__main__":
    analyzer = BuyPointInvestigation()
    stockDao = StockDao()
    stocks = stockDao.getStockList()

    # rps120 > 90 的股票
    stockBarDao = StockDailyBarAdjustPrevDao()
    bars = stockBarDao.getByDate('2019-01-23')
    print(bars[0])
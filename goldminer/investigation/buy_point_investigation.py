# coding: utf-8
from goldminer.storage.StockDao import StockDao
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao


class BuyPointInvestigation:
    def __init__(self):
        self.stockFundamentals = StockFundamentalsDao()




if __name__ == "__main__":
    analyzer = BuyPointInvestigation()
    stockDao = StockDao()
    stocks = stockDao.getStockList()
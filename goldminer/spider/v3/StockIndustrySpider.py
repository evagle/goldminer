# coding: utf-8

from goldminer.common.logger import get_logger
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.IndustryDao import IndustryDao
from goldminer.storage.StockDao import StockDao

'''
从掘金的getIndustry接口下载stock的industy数据
tushare的数据质量太低
'''

logger = get_logger(__name__)


class StockIndustrySpider(GMBaseSpiderV3):
    def __init__(self):
        super(StockIndustrySpider, self).__init__()
        self.stockDao = StockDao()
        self.industryDao = IndustryDao()

    def updateIndustry(self):
        industries = self.industryDao.all()
        logger.info("[StockIndustrySpider] Get {} industries.".format(len(industries)))

        stockIndustryMap = {}
        for industry in industries:
            stocks = self.getIndustry(industry.code)
            logger.info("[StockIndustrySpider] Stocks in industry {} are {}.".format(industry.name, stocks))
            for code in stocks:
                code = code[5:]
                if code not in stockIndustryMap:
                    stockIndustryMap[code] = []
                stockIndustryMap[code].append(industry.code)

        stocksExistsDB = self.stockDao.all()
        stocksDict = {}
        for stock in stocksExistsDB:
            stocksDict[stock.code] = stock

        updatedStock = []
        for code in stockIndustryMap:
            if code not in stocksDict:
                continue
            stock = stocksDict[code]
            stock.industry = ",".join(stockIndustryMap[code])
            updatedStock.append(stock)
            logger.info("[StockIndustrySpider] Add industry {} for stock {}.".format(stock.industry, stock))

        if len(updatedStock) > 0:
            self.stockDao.bulkSave(updatedStock)
            logger.info("[StockIndustrySpider] Update industry for {} stocks.".format(len(updatedStock)))


if __name__ == "__main__":
    spider = StockIndustrySpider()
    spider.updateIndustry()

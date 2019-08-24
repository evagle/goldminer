# coding: utf-8
from datetime import datetime

import tushare as ts

from goldminer.common.logger import get_logger
from goldminer.models.models import Stock
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class StockSpider():
    def __init__(self):
        super(StockSpider, self).__init__()
        self.stockDao = StockDao()

    '''
    从tushare下载所有股票列表，更新stock数据库
    '''
    def getStockFromTuShare(self):
        logger.info("[StockSpider] Start to update stock list")
        data = ts.get_stock_basics()
        logger.info("[StockSpider] Get {} stocks from tushare.".format(data.shape[0]))

        stocksExistsDB = self.stockDao.all()
        stocksDict = {}
        for stock in stocksExistsDB:
            stocksDict[stock.code] = stock
        logger.info("[StockSpider] Get {} stocks from db.".format(len(stocksExistsDB)))

        newStocks = []
        for code, row in data.iterrows():
            if code not in stocksDict and not row["name"].startswith("N") and row.timeToMarket > 0:
                stock = Stock()
                stock.code = code
                stock.name = row["name"]
                stock.pub_date = datetime.strptime(str(row.timeToMarket), "%Y%m%d")
                stock.end_date = None
                stock.industry = ""
                if code[0:1] == "6":
                    stock.exchange = 1
                else:
                    stock.exchange = 2
                stock.total_stock = row.totals*1e8
                stock.circulation_stock = row.outstanding*1e8
                newStocks.append(stock)
                logger.info("[StockSpider] New stock {}".format(stock))

        self.stockDao.bulkSave(newStocks)
        logger.info("[StockSpider] Save {} new stocks to db.".format(len(newStocks)))

    '''
    从上交所下载股票列表然后导入
    下载地址
    http://www.sse.com.cn/assortment/stock/list/share/
    '''
    def importFromSH(self):
        dao = StockDao()
        for line in open("/Users/abing/Downloads/ee.txt").readlines():
            args = line.split()

            old = dao.getByCode(args[0])
            if old is None:
                stock = Stock()
                stock.exchange = 1
                stock.code = args[0]
                stock.name = args[1]
                stock.pub_date = args[4]
                stock.total_stock = args[5]
                stock.circulation_stock = args[6]
                stock.industry = ''
                dao.add(stock)
                print(args)


if __name__ == "__main__":
    spider = StockSpider()
    spider.getStockFromTuShare()



# coding: utf-8
from datetime import datetime

import tushare as ts
from goldminer.spider.tushare.TushareBase import TushareBase

from goldminer.common.logger import get_logger
from goldminer.models.models import Stock
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class StockSpider(TushareBase):
    def __init__(self):
        super(StockSpider, self).__init__()
        self.stockDao = StockDao()
        self.exchangeMap = {"SSE": 1, "SZSE": 2}

    def _diff(self, stockA, stockB):
        fields = ["code", 'pub_date', 'end_date', 'exchange', 'status']
        changed = False
        for field in fields:
            if getattr(stockA, field) != getattr(stockB, field):
                changed = True
                break
        if changed:
            for field in fields:
                setattr(stockA, field, getattr(stockB, field))
            return stockA
        else:
            return None

    def getStockFromTuShare(self):
        """
        从tushare下载所有股票列表，更新stock数据库
        """
        logger.info("[StockSpider] Start to update stock list")
        data = self.ts_pro_api.stock_basic(fields='ts_code,symbol,name,area,industry,list_date,delist_date,list_status,exchange')
        logger.info("[StockSpider] Get {} stocks from tushare.".format(data.shape[0]))

        stocksInDB = self.stockDao.all()
        stocksDict = {}
        for stock in stocksInDB:
            stocksDict[stock.code] = stock
        logger.info("[StockSpider] Get {} stocks from db.".format(len(stocksInDB)))

        newStocks = []
        for _, row in data.iterrows():
            code = row["symbol"]
            name = row["name"]
            list_date = datetime.strptime(row["list_date"], "%Y%m%d").date()
            if name.startswith("N") or list_date is None:
                continue
            stock = Stock()
            stock.code = code
            stock.name = name
            stock.pub_date = list_date
            delist_date = row["delist_date"]
            if delist_date is not None:
                stock.end_date = datetime.strptime(delist_date, "%Y%m%d").date()
            # industry用掘金的数据
            if code in stocksDict:
                stock.industry = stocksDict[code].industry
            stock.exchange = self.exchangeMap[row["exchange"]]
            stock.status = row["list_status"]

            if code not in stocksDict:
                newStocks.append(stock)
                logger.info("[StockSpider] New stock {}".format(stock))
            else:
                updatedStock = self._diff(stocksDict[code], stock)
                if updatedStock:
                    newStocks.append(updatedStock)
                    logger.info("[StockSpider] Update stock {}".format(updatedStock))

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



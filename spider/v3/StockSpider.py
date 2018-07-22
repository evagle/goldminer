# coding: utf-8
import json
from datetime import datetime

import tushare as ts
import pandas as pd

from models.models import Stock
from storage.IndustryDao import IndustryDao
from storage.StockDao import StockDao


class StockSpider():
    def __init__(self):
        super(StockSpider, self).__init__()
        self.stockDao = StockDao()

    def getStockFromTuShare(self):
        data = ts.get_stock_basics()
        for code, row in data.iterrows():
            print(code)
            # print(row)
            stock = self.stockDao.getByCode(code)
            if not stock and not row["name"].startswith("N") and row.timeToMarket > 0:
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
                self.stockDao.add(stock)
                print(stock)


if __name__ == "__main__":
    spider = StockSpider()
    spider.getStockFromTuShare()



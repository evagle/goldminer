# coding: utf-8

from typing import List

from models.models import Stock
from storage.BaseDao import BaseDao


class StockDao(BaseDao):

    def all(self) -> List[Stock]:
        return self.session.query(Stock).all()

    def getByCode(self, code) -> Stock:
        return self.session.query(Stock).filter(Stock.code == code).first()

    def getStockList(self) -> List[str]:
        result = self.session.query(Stock.code).all()
        return [i[0] for i in result]

    def add(self, stock: Stock):
        self.session.add(stock)
        self.session.commit()

    # get stock publish date, return None when stock not fund
    def getStockPublishDate(self, code: str):
        result = self.session.query(Stock.pub_date).filter(Stock.code == code).first()
        if result is not None:
            return result[0]
        return None


'''
从上交所下载股票列表然后导入
'''
def importFromSH():
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
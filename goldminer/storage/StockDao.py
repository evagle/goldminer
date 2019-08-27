# coding: utf-8

from typing import List

from goldminer.models.models import Stock
from goldminer.storage.BaseDao import BaseDao


class StockDao(BaseDao):

    def all(self) -> List[Stock]:
        return self.session.query(Stock).all()

    def getByCode(self, code) -> Stock:
        return self.session.query(Stock).filter(Stock.code == code).first()

    def getStockList(self) -> List[str]:
        result = self.session.query(Stock.code).filter(Stock.end_date.is_(None)).all()
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

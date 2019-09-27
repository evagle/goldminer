# coding: utf-8

from typing import List

from goldminer.models.models import Stock
from goldminer.storage.BaseDao import BaseDao


class StockDao(BaseDao):

    def all(self) -> List[Stock]:
        return self.session.query(Stock).all()

    def getByCode(self, code) -> Stock:
        return self.session.query(Stock).filter(Stock.code == code).first()

    def getStockList(self, includeB=False, includeDelisted=False) -> List[str]:
        """
        Retrieve stock code list
        :param includeDelisted: return delisted stocks if true
        :param includeB: whether to include B stock
        :return: stock code list
        """
        query = self.session.query(Stock.code)
        if not includeDelisted:
            query = query.filter(Stock.end_date.is_(None))

        result = query.all()
        codes = [i[0] for i in result]
        if not includeB:
            codesA = []
            for code in codes:
                if code[0] != "9":
                    codesA.append(code)
            return codesA
        else:
            return codes

    def add(self, stock: Stock):
        self.session.add(stock)
        self.session.commit()

    # get stock publish date, return None when stock not fund
    def getStockPublishDate(self, code: str):
        result = self.session.query(Stock.pub_date).filter(Stock.code == code).first()
        if result is not None:
            return result[0]
        return None

    def getAllStockPublishDate(self):
        result = self.session.query(Stock.code, Stock.pub_date).all()

        if result is not None:
            dic = {}
            for i in result:
                dic[i[0]] = i[1]
            return dic
        return None

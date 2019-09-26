# coding: utf-8
from datetime import date, datetime

from goldminer.models.models import IndexConstituent
from goldminer.storage.BaseDao import BaseDao


class IndexConstituentDao(BaseDao):

    def add(self, constituent: IndexConstituent):
        constituent.constituents = constituent.constituents.replace("'", "\"")
        self.session.add(constituent)
        self.session.commit()

    def addAll(self, constituents):
        for constituent in constituents:
            constituent.constituents = constituent.constituents.replace("'", "\"")
        super(IndexConstituentDao, self).addAll(constituents)

    def getLatestDate(self, code: str):
        result = self.session.query(IndexConstituent.trade_date) \
            .filter(IndexConstituent.code == code) \
            .order_by(IndexConstituent.trade_date.desc()) \
            .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getByDate(self, code: str, tradeDate) -> IndexConstituent:
        return self.session.query(IndexConstituent) \
            .filter(IndexConstituent.code == code, IndexConstituent.trade_date == tradeDate) \
            .first()

    def getConstituentUpdateDates(self, code):
        return self.session.query(IndexConstituent.trade_date) \
            .filter(IndexConstituent.code == code) \
            .order_by(IndexConstituent.trade_date.asc())\
            .all()

    '''
    1. Find first record with trade_date <= date
    2. If date < all trade_date, return first one
    '''
    def getConstituents(self, code, tradeDate) -> IndexConstituent:
        result = self.session.query(IndexConstituent) \
                             .filter(IndexConstituent.code == code, IndexConstituent.trade_date <= tradeDate) \
                             .order_by(IndexConstituent.trade_date.desc()) \
                             .first()
        if result is not None and (tradeDate - result.trade_date).days < 200:
            return result

        result = self.session.query(IndexConstituent) \
            .filter(IndexConstituent.code == code, IndexConstituent.trade_date > tradeDate) \
            .order_by(IndexConstituent.trade_date.asc()) \
            .first()

        if result is not None and (result.trade_date - tradeDate).days < 200:
            return result
        else:
            return None

    def getConstituentsBeforeDate(self, code, tradeDate) -> IndexConstituent:
        return self.session.query(IndexConstituent) \
                             .filter(IndexConstituent.code == code, IndexConstituent.trade_date <= tradeDate) \
                             .order_by(IndexConstituent.trade_date.desc()) \
                             .first()


if __name__ == "__main__":
    constituentDao = IndexConstituentDao()
    print(constituentDao.getConstituents('399006', date(2012, 1, 1)))
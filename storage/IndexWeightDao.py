# coding: utf-8
from datetime import date

from models.models import IndexWeight
from storage.BaseDao import BaseDao


class IndexWeightDao(BaseDao):

    def add(self, constituent: IndexWeight):
        constituent.constituents = constituent.constituents.replace("'", "\"")
        self.session.add(constituent)
        self.session.commit()

    def addAll(self, constituents):
        for constituent in constituents:
            constituent.constituents = constituent.constituents.replace("'", "\"")
        super(IndexWeightDao, self).addAll(constituents)

    def getLatestDate(self, code: str):
        result = self.session.query(IndexWeight.trade_date) \
            .filter(IndexWeight.code == code) \
            .order_by(IndexWeight.trade_date.desc()) \
            .first()
        return date(2001, 1, 1) if result is None else result[0]

    '''
    1. Find first record with trade_date >= date
    2. If date > all record, return latest one
    '''
    def getConstituents(self, code, tradeDate) -> IndexWeight:
        result = self.session.query(IndexWeight) \
                             .filter(IndexWeight.code == code, IndexWeight.trade_date >= tradeDate) \
                             .order_by(IndexWeight.trade_date.asc()) \
                             .first()
        if result is not None:
            return result

        result = self.session.query(IndexWeight) \
            .filter(IndexWeight.code == code, IndexWeight.trade_date < tradeDate) \
            .order_by(IndexWeight.trade_date.desc()) \
            .first()
        return result

    '''
    1. Find first record with trade_date <= date
    2. If date < all trade_date, return first one
    '''
    def getConstituents_1(self, code, tradeDate) -> IndexWeight:
        result = self.session.query(IndexWeight) \
                             .filter(IndexWeight.code == code, IndexWeight.trade_date <= tradeDate) \
                             .order_by(IndexWeight.trade_date.desc()) \
                             .first()
        if result is not None:
            return result

        result = self.session.query(IndexWeight) \
            .filter(IndexWeight.code == code, IndexWeight.trade_date > tradeDate) \
            .order_by(IndexWeight.trade_date.asc()) \
            .first()
        return result



if __name__ == "__main__":
    constituentDao = IndexWeightDao()
    print(constituentDao.getConstituents('000001', date(2005, 1, 1)))
# coding: utf-8
from datetime import date

from models.models import IndexConstituent
from storage.BaseDao import BaseDao


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

    '''
    1. Find first record with trade_date <= date
    2. If date < all trade_date, return first one
    '''
    # TODO if date is too earlier more than 1 year than first trade_date, better to return None
    def getConstituents(self, code, tradeDate) -> IndexConstituent:
        result = self.session.query(IndexConstituent) \
                             .filter(IndexConstituent.code == code, IndexConstituent.trade_date <= tradeDate) \
                             .order_by(IndexConstituent.trade_date.desc()) \
                             .first()
        if result is not None:
            return result

        result = self.session.query(IndexConstituent) \
            .filter(IndexConstituent.code == code, IndexConstituent.trade_date > tradeDate) \
            .order_by(IndexConstituent.trade_date.asc()) \
            .first()
        return result



if __name__ == "__main__":
    constituentDao = IndexConstituentDao()
    print(constituentDao.getConstituents('000001', date(2005, 1, 1)))
# coding: utf-8
from datetime import date

from models.models import IndexConstituent
from storage.BaseDao import BaseDao


class IndexConstituentDao(BaseDao):

    def add(self, constituent: IndexConstituent):
        self.session.add(constituent)
        self.session.commit()

    def addAll(self, constituents):
        self.session.add_all(constituents)
        self.session.commit()

    def getLatestDate(self, code: str):
        result = self.session.query(IndexConstituent.trade_date)\
                             .filter(IndexConstituent.code == code)\
                             .order_by(IndexConstituent.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

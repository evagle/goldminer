# coding: utf-8
from datetime import date

from models.models import IndexDailyBar
from storage.BaseDao import BaseDao


class StockFundamentalsDao(BaseDao):

    def add(self, item):
        self.session.add(item)
        self.session.commit()

    def addAll(self, items):
        self.session.add_all(items)
        self.session.commit()

    def getLatestDate(self, code: str, modelClass):
        result = self.session.query(modelClass.end_date)\
                             .filter(modelClass.code == code)\
                             .order_by(modelClass.end_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

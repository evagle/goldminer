# coding: utf-8
from datetime import date

from models.models import IndexDailyBar
from storage.BaseDao import BaseDao


class StockFundamentalsDao(BaseDao):

    def add(self, model):
        self.session.add(model)
        self.session.commit()

    def addAll(self, models):
        if len(models) == 0:
            return
        clazz = models[0].__class__
        self._addAll(clazz, models)

    def getLatestDate(self, code: str, modelClazz):
        result = self.session.query(modelClazz.end_date)\
                             .filter(modelClazz.code == code)\
                             .order_by(modelClazz.end_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

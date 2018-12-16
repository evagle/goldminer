# coding: utf-8
from datetime import date

from goldminer.storage.BaseDao import BaseDao

class StockFundamentalsDao(BaseDao):

    def add(self, model):
        self.session.add(model)
        self.session.commit()

    def getLatestDate(self, code: str, modelClazz):
        result = self.session.query(modelClazz.end_date)\
                             .filter(modelClazz.code == code)\
                             .order_by(modelClazz.end_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getAll(self, code: str, modelClazz):
        result = self.session.query(modelClazz) \
            .filter(modelClazz.code == code) \
            .order_by(modelClazz.end_date.asc()) \
            .all()
        return result

    def getByDate(self, code: str, tradeDate: date, modelClazz):
        result = self.session.query(modelClazz) \
            .filter(modelClazz.code == code, modelClazz.end_date == tradeDate) \
            .first()
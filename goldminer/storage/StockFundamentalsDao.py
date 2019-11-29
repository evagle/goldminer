# coding: utf-8
from datetime import date

import sqlalchemy
from sqlalchemy.orm import aliased

from goldminer.storage.BaseDao import BaseDao


class StockFundamentalsDao(BaseDao):

    def add(self, model):
        self.session.add(model)
        self.session.commit()

    def getLatestDate(self, code: str, modelClazz):
        result = self.session.query(modelClazz.pub_date)\
                             .filter(modelClazz.code == code)\
                             .order_by(modelClazz.pub_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getLatestDateByCodes(self, codes: list, modelClazz):
        tableA = aliased(modelClazz, name="a")
        tableB = aliased(modelClazz, name="b")
        result = self.session.query(tableA.pub_date)\
                             .filter(tableA.code.in_(codes), tableA.pub_date == self.session.query(sqlalchemy.func.max(tableB.pub_date))\
                                                            .filter(tableB.code == tableA.code))\
                             .order_by(tableA.pub_date.asc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getAll(self, code: str, modelClazz):
        result = self.session.query(modelClazz) \
            .filter(modelClazz.code == code) \
            .order_by(modelClazz.end_date.asc()) \
            .all()
        return result

    def getBatch(self, codes: list, modelClazz):
        result = self.session.query(modelClazz) \
            .filter(modelClazz.code.in_(codes)) \
            .order_by(modelClazz.end_date.asc()) \
            .all()
        return result

# coding: utf-8
from datetime import date, timedelta
from typing import List

from sqlalchemy import Column

from models.models import IndexPrimaryIndicator
from storage.BaseDao import BaseDao


class IndexPrimaryIndicatorDao(BaseDao):

    def __init__(self):
        super(IndexPrimaryIndicatorDao, self).__init__()

    def getByCode(self, code: str) -> List[IndexPrimaryIndicator]:
        return self.session.query(IndexPrimaryIndicator) \
                            .filter(IndexPrimaryIndicator.code == code) \
                            .order_by(IndexPrimaryIndicator.trade_date.asc())\
                            .all()

    def getLatestDate(self, code: str, columnName):
        result = self.session.query(IndexPrimaryIndicator.trade_date)\
                             .filter(IndexPrimaryIndicator.code == code)\
                             .filter(Column(columnName).isnot(None))\
                             .order_by(IndexPrimaryIndicator.trade_date.desc())\
                             .first()

        return date(2005, 1, 4) if result is None else result[0]

    def getByDate(self, code, tradeDate: date):
        clazzName = IndexPrimaryIndicator.__name__
        val = self.getFromCache(code, tradeDate, clazzName)
        if val is not None:
            return val
        self.deleteCache(clazzName)

        results = self.session.query(IndexPrimaryIndicator)\
                              .filter(IndexPrimaryIndicator.code == code)\
                              .filter(IndexPrimaryIndicator.trade_date >= tradeDate, IndexPrimaryIndicator.trade_date <= tradeDate + timedelta(days=60))\
                              .all()

        self.addToCache(code, clazzName, results)
        return self.getFromCache(code, tradeDate, clazzName)

    def getAfterDate(self, code, tradeDate: date) -> List[IndexPrimaryIndicator]:
        return self.session.query(IndexPrimaryIndicator)\
                            .filter(IndexPrimaryIndicator.code == code)\
                            .filter(IndexPrimaryIndicator.trade_date >= tradeDate) \
                            .order_by(IndexPrimaryIndicator.trade_date.asc())\
                            .all()

    def bulkUpdateMappings(self, clazz, mappings: List [dict]):
        self.session.bulk_update_mappings(clazz, mappings)
        self.session.commit()

    def bulkSave(self, models):
        self.session.bulk_save_objects(models)
        self.session.commit()
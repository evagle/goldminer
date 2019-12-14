# coding: utf-8
from datetime import date, timedelta
from typing import List, Dict

from sqlalchemy import Column

from goldminer.models.models import IndexPrimaryIndicator
from goldminer.storage.BaseDao import BaseDao


class IndexPrimaryIndicatorDao(BaseDao):

    def __init__(self):
        super(IndexPrimaryIndicatorDao, self).__init__()

    def getByCode(self, code: str) -> List[IndexPrimaryIndicator]:
        return self.session.query(IndexPrimaryIndicator) \
            .filter(IndexPrimaryIndicator.code == code) \
            .order_by(IndexPrimaryIndicator.trade_date.asc()) \
            .all()

    def getByCodeDict(self, code: str) -> Dict[tuple, IndexPrimaryIndicator]:
        """
        Get all IndexPrimaryIndicator for code and return in dict format
        :param code:
        :return: Dict
        {
            tuple(code, trade_date): IndexPrimaryIndicator
        }
        """
        result = self.getByCode(code)
        dic = {}
        for model in result:
            dic[(model.code, model.trade_date)] = model
        return dic

    def getLatestDate(self, code: str, columnName):
        result = self.session.query(IndexPrimaryIndicator.trade_date) \
            .filter(IndexPrimaryIndicator.code == code) \
            .filter(Column(columnName).isnot(None)) \
            .order_by(IndexPrimaryIndicator.trade_date.desc()) \
            .first()

        return None if result is None else result[0]

    def getByDate(self, code, tradeDate: date) -> IndexPrimaryIndicator:
        clazzName = IndexPrimaryIndicator.__name__
        val = self.getFromCache(code, tradeDate, clazzName)
        if val is not None:
            return val
        self.deleteCache(clazzName)

        results = self.session.query(IndexPrimaryIndicator) \
            .filter(IndexPrimaryIndicator.code == code) \
            .filter(IndexPrimaryIndicator.trade_date >= tradeDate,
                    IndexPrimaryIndicator.trade_date <= tradeDate + timedelta(days=60)) \
            .all()

        self.addToCache(code, clazzName, results)
        return self.getFromCache(code, tradeDate, clazzName)

    def getAfterDate(self, code, tradeDate: date) -> List[IndexPrimaryIndicator]:
        return self.session.query(IndexPrimaryIndicator) \
            .filter(IndexPrimaryIndicator.code == code) \
            .filter(IndexPrimaryIndicator.trade_date >= tradeDate) \
            .order_by(IndexPrimaryIndicator.trade_date.asc()) \
            .all()

    def bulkUpdateMappings(self, clazz, mappings: List[dict]):
        self.session.bulk_update_mappings(clazz, mappings)
        self.session.commit()

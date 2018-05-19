# coding: utf-8
from datetime import date
from typing import List

from sqlalchemy import Column

from models.models import IndexPrimaryIndicator
from storage.BaseDao import BaseDao


class IndexPrimaryIndicatorDao(BaseDao):

    def getLatestDate(self, code: str, columnName):
        result = self.session.query(IndexPrimaryIndicator.trade_date)\
                             .filter(IndexPrimaryIndicator.code == code)\
                             .filter(Column(columnName).isnot(None))\
                             .order_by(IndexPrimaryIndicator.trade_date.desc())\
                             .first()

        return date(2005, 1, 4) if result is None else result[0]

    def getByDate(self, code, tradeDate: date):
        return self.session.query(IndexPrimaryIndicator)\
                            .filter(IndexPrimaryIndicator.code == code)\
                            .filter(IndexPrimaryIndicator.trade_date == tradeDate)\
                            .first()

    def bulkUpdateMappings(self, clazz, mappings: List [dict]):
        self.session.bulk_update_mappings(clazz, mappings)
        self.session.commit()

    def bulkSave(self, models):
        self.session.bulk_save_objects(models)
        self.session.commit()
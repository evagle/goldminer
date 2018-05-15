# coding: utf-8
from datetime import date

from models.models import IndexPrimaryIndicator
from storage.BaseDao import BaseDao
from sqlalchemy.sql import column


class IndexPrimaryIndicatorDao(BaseDao):

    def getLatestDate(self, code: str, columnName):
        result = self.session.query(IndexPrimaryIndicator.trade_date)\
                             .filter(IndexPrimaryIndicator.code == code)\
                             .filter_by(column(columnName).isnot(None))\
                             .order_by(IndexPrimaryIndicator.trade_date.desc())\
                             .first()

        return date(2005, 1, 4) if result is None else result[0]

    def batchUpdate(self, models):
        self.session.bulk_save_objects(models)

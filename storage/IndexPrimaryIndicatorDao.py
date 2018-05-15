# coding: utf-8
from datetime import date

from models.models import IndexDailyBar, IndexPrimaryIndicator
from storage.BaseDao import BaseDao


class IndexPrimaryIndicatorDao(BaseDao):

    def add(self, indicator: IndexPrimaryIndicator):
        self.session.add(indicator)
        self.session.commit()

    def getLatestDate(self, code: str):
        result = self.session.query(IndexPrimaryIndicator.trade_date)\
                             .filter(IndexPrimaryIndicator.code == code)\
                             .order_by(IndexPrimaryIndicator.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

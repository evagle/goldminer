# coding: utf-8
from datetime import date

from models.models import IndexDailyBar
from storage.BaseDao import BaseDao


class IndexDailyBarDao(BaseDao):

    def add(self, indexBar: IndexDailyBar):
        self.session.add(indexBar)
        self.session.commit()

    def getLatestDate(self, code: str):
        result = self.session.query(IndexDailyBar.trade_date)\
                             .filter(IndexDailyBar.code == code)\
                             .order_by(IndexDailyBar.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

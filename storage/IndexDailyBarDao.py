# coding: utf-8
from datetime import date

from models.models import IndexDailyBar
from storage.BaseDao import BaseDao


class IndexDailyBarDao(BaseDao):

    def add(self, indexBar: IndexDailyBar):
        self.session.add(indexBar)
        self.session.commit()

    def getByDate(self, code, d: date) -> IndexDailyBar:
        return self.session.query(IndexDailyBar) \
            .filter(IndexDailyBar.code == code) \
            .filter(IndexDailyBar.trade_date == d) \
            .first()

    def getLatestDate(self, code):
        result = self.session.query(IndexDailyBar.trade_date)\
                             .filter(IndexDailyBar.code == code)\
                             .order_by(IndexDailyBar.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getByCode(self, code):
        result = self.session.query(IndexDailyBar) \
            .filter(IndexDailyBar.code == code) \
            .order_by(IndexDailyBar.trade_date.asc()) \
            .all()
        return result

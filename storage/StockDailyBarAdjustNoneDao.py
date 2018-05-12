# coding: utf-8
from datetime import date

from models.models import StockDailyBarAdjustNone
from storage.BaseDao import BaseDao


class StockDailyBarAdjustNoneDao(BaseDao):

    def add(self, stockBar: StockDailyBarAdjustNone):
        self.session.add(stockBar)
        self.session.commit()

    def addAll(self, stockBars):
        self.session.add_all(stockBars)
        self.session.commit()

    def getLatestDate(self, code: str):
        result = self.session.query(StockDailyBarAdjustNone.trade_date)\
                             .filter(StockDailyBarAdjustNone.code == code)\
                             .order_by(StockDailyBarAdjustNone.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]


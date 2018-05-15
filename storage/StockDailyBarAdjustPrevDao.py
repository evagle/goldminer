# coding: utf-8
from datetime import date

from models.models import StockDailyBarAdjustPrev
from storage.BaseDao import BaseDao


class StockDailyBarAdjustPrevDao(BaseDao):

    def add(self, stockBar: StockDailyBarAdjustPrev):
        self.session.add(stockBar)
        self.session.commit()

    def addAll(self, stockBars):
        self._addAll(StockDailyBarAdjustPrev, stockBars)

    def getLatestDate(self, code: str):
        result = self.session.query(StockDailyBarAdjustPrev.trade_date)\
                             .filter(StockDailyBarAdjustPrev.code == code)\
                             .order_by(StockDailyBarAdjustPrev.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

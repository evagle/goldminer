# coding: utf-8
from datetime import date

from goldminer.models.models import StockDailyBarAdjustPrev
from goldminer.storage.BaseDao import BaseDao
from typing import List

class StockDailyBarAdjustPrevDao(BaseDao):

    def add(self, stockBar: StockDailyBarAdjustPrev):
        self.session.add(stockBar)
        self.session.commit()

    def getLatestDate(self, code: str):
        result = self.session.query(StockDailyBarAdjustPrev.trade_date)\
                             .filter(StockDailyBarAdjustPrev.code == code)\
                             .order_by(StockDailyBarAdjustPrev.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getAll(self, code: str) -> List[StockDailyBarAdjustPrev]:
        result = self.session.query(StockDailyBarAdjustPrev) \
            .filter(StockDailyBarAdjustPrev.code == code) \
            .order_by(StockDailyBarAdjustPrev.trade_date.asc()) \
            .all()
        return result
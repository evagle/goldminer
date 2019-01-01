# coding: utf-8
from datetime import date

from goldminer.models.models import StockDailyBarAdjustNone
from goldminer.storage.BaseDao import BaseDao
from typing import List

class StockDailyBarAdjustNoneDao(BaseDao):

    def add(self, stockBar: StockDailyBarAdjustNone):
        self.session.add(stockBar)
        self.session.commit()

    def getLatestDate(self, code: str):
        result = self.session.query(StockDailyBarAdjustNone.trade_date)\
                             .filter(StockDailyBarAdjustNone.code == code)\
                             .order_by(StockDailyBarAdjustNone.trade_date.desc())\
                             .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getAllTradeDatesByCode(self, code: str):
        result = self.session.query(StockDailyBarAdjustNone.trade_date)\
                             .filter(StockDailyBarAdjustNone.code == code)\
                             .order_by(StockDailyBarAdjustNone.trade_date.asc())\
                             .all()
        return [d[0] for d in result]

    def getAll(self, code: str) -> List[StockDailyBarAdjustNone]:
        return self.getN(code)

    def getN(self, code: str, limit = None) -> List[StockDailyBarAdjustNone]:
        query = self.session.query(StockDailyBarAdjustNone) \
            .filter(StockDailyBarAdjustNone.code == code) \
            .order_by(StockDailyBarAdjustNone.trade_date.asc())
        if limit is None or limit <= 0:
            result = query.all()
        else:
            result = query.limit(limit).all()
        return result

    def getByDate(self, trade_date: str) -> List[StockDailyBarAdjustNone]:
        result = self.session.query(StockDailyBarAdjustNone) \
            .filter(StockDailyBarAdjustNone.trade_date == trade_date) \
            .order_by(StockDailyBarAdjustNone.code.asc()) \
            .all()
        return result


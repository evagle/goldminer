# coding: utf-8
from datetime import date

from goldminer.common.Utils import Utils

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

    def getByCode(self, code: str, adjust="prev") -> List[StockDailyBarAdjustNone]:
        bars = self.getN(code, adjust=adjust)
        return bars

    def getN(self, code: str, limit = None, adjust="prev") -> List[StockDailyBarAdjustNone]:
        """
        Fetch top N(N=limit) records ordered by trade_date desc
        :param code:
        :param limit:
        :param adjust:
        :return:
        """
        query = self.session.query(StockDailyBarAdjustNone) \
            .filter(StockDailyBarAdjustNone.code == code) \
            .order_by(StockDailyBarAdjustNone.trade_date.desc())
        if limit is None or limit <= 0:
            result = query.all()
        else:
            result = query.limit(limit).all()

        if adjust == "prev":
            result = Utils.pre_adjust(result)
        return result

    def getByDate(self, trade_date: str) -> List[StockDailyBarAdjustNone]:
        result = self.session.query(StockDailyBarAdjustNone) \
            .filter(StockDailyBarAdjustNone.trade_date == trade_date) \
            .order_by(StockDailyBarAdjustNone.code.asc()) \
            .all()
        return result


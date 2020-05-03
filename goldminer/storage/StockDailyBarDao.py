# coding: utf-8
from datetime import date
from decimal import Decimal
from typing import List

from goldminer.models.models import StockDailyBar
from goldminer.storage.BaseDao import BaseDao


class StockDailyBarDao(BaseDao):

    def add(self, stockBar: StockDailyBar):
        self.session.add(stockBar)
        self.session.commit()

    def getLatestDate(self, code: str):
        result = self.session.query(StockDailyBar.trade_date) \
            .filter(StockDailyBar.code == code) \
            .order_by(StockDailyBar.trade_date.desc()) \
            .first()
        return date(2001, 1, 1) if result is None else result[0]

    def getAllTradeDatesByCode(self, code: str):
        result = self.session.query(StockDailyBar.trade_date) \
            .filter(StockDailyBar.code == code) \
            .order_by(StockDailyBar.trade_date.asc()) \
            .all()
        return [d[0] for d in result]

    def getByCode(self, code: str, adjust="prev") -> List[StockDailyBar]:
        bars = self.getN(code, adjust=adjust)
        return bars

    def getN(self, code: str, limit=None, adjust="prev") -> List[StockDailyBar]:
        """
        Fetch top N(N=limit) records ordered by trade_date desc
        :param code:
        :param limit:
        :param adjust:
        :return:
        """
        query = self.session.query(StockDailyBar) \
            .filter(StockDailyBar.code == code) \
            .order_by(StockDailyBar.trade_date.desc())
        if limit is None or limit <= 0:
            result = query.all()
        else:
            result = query.limit(limit).all()
        result = sorted(result, key=lambda x: x.trade_date, reverse=False)

        if adjust is not None and adjust == "prev":
            result = StockDailyBarDao.pre_adjust(result)
        return result

    def getByDate(self, trade_date: str) -> List[StockDailyBar]:
        result = self.session.query(StockDailyBar) \
            .filter(StockDailyBar.trade_date == trade_date) \
            .order_by(StockDailyBar.code.asc()) \
            .all()
        return result

    def getAdjFactor(self, code) :
        result = self.session.query(StockDailyBar.code, StockDailyBar.trade_date, StockDailyBar.adj_factor) \
            .filter(StockDailyBar.code == code) \
            .all()
        return result

    def delete_by_code(self, code: str):
        if not code:
            return 0

        self.session.query(StockDailyBar).filter(StockDailyBar.code == code).delete()
        return self.session.commit()

    @staticmethod
    def pre_adjust(bars):
        if bars is None or isinstance(bars, list) or len(bars) == 0:
            return bars

        factor = bars[-1].adj_factor
        pre_adjusted_bars = []
        for bar in bars:
            new_bar = StockDailyBar(constructor=None)
            new_bar.code = bar.code
            new_bar.trade_date = bar.trade_date
            new_bar.amount = bar.amount
            new_bar.volume = bar.volume
            new_bar.is_suspended = bar.is_suspended
            new_bar.adj_factor = bar.adj_factor
            new_bar.high = float(Decimal(bar.high) * bar.adj_factor / factor)
            new_bar.low = float(Decimal(bar.low) * bar.adj_factor / factor)
            new_bar.close = float(Decimal(bar.close) * bar.adj_factor / factor)
            new_bar.open = float(Decimal(bar.open) * bar.adj_factor / factor)
            new_bar.pre_close = float(Decimal(bar.pre_close) * bar.adj_factor / factor)

            pre_adjusted_bars.append(new_bar)

        return pre_adjusted_bars

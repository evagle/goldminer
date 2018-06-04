# coding: utf-8
from datetime import date
from typing import List

from models.models import SalaryFund, FundDailyBar
from storage.BaseDao import BaseDao


class FundDailyBarDao(BaseDao):

    def all(self) -> List[FundDailyBar]:
        return self.session.query(FundDailyBar).all()

    def add(self, bar: FundDailyBar):
        self.session.add(bar)
        self.session.commit()

    def getByDate(self, code, tradeDate: date):
        return self.session.query(FundDailyBar) \
            .filter(FundDailyBar.code == code) \
            .filter(FundDailyBar.trade_date == tradeDate) \
            .first()

    def getLatestTradeDate(self, code):
        result = self.session.query(FundDailyBar) \
            .filter(FundDailyBar.code == code) \
            .order_by(FundDailyBar.trade_date.desc()) \
            .first()
        if result is not None:
            return result.trade_date
        return date(2017, 1, 1)



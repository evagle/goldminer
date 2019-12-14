# coding: utf-8
from datetime import date
from typing import List

from goldminer.models.models import SalaryFund
from goldminer.storage.BaseDao import BaseDao


class SalaryFundDao(BaseDao):

    def all(self) -> List[SalaryFund]:
        return self.session.query(SalaryFund).all()

    def add(self, model: SalaryFund):
        self.session.add(model)
        self.session.commit()

    def getByDate(self, tradeDate: date):
        return self.session.query(SalaryFund) \
            .filter(SalaryFund.trade_date == tradeDate) \
            .first()

    def getLatestDate(self):
        result = self.session.query(SalaryFund.trade_date) \
            .order_by(SalaryFund.trade_date.desc()) \
            .first()
        return None if result is None else result[0]

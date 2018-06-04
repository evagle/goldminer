# coding: utf-8
from datetime import date
from typing import List

from models.models import SalaryFund
from storage.BaseDao import BaseDao


class SalaryFundDao(BaseDao):

    def all(self) -> List[SalaryFund]:
        return self.session.query(SalaryFund).all()

    def add(self, model: SalaryFund):
        self.session.add(model)
        self.session.commit()

    def getByDate(self, code, tradeDate: date):
        return self.session.query(SalaryFund) \
            .filter(SalaryFund.code == code) \
            .filter(SalaryFund.trade_date == tradeDate) \
            .first()

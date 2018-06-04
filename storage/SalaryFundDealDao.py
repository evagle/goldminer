# coding: utf-8
from datetime import date
from typing import List

from sqlalchemy import distinct

from models.models import SalaryFund, SalaryFundDeal
from storage.BaseDao import BaseDao


class SalaryFundDealDao(BaseDao):

    def all(self) -> List[SalaryFundDeal]:
        return self.session.query(SalaryFundDeal).all()

    def add(self, model: SalaryFundDeal):
        self.session.add(model)
        self.session.commit()

    def getByDate(self, code, tradeDate: date):
        return self.session.query(SalaryFundDeal) \
            .filter(SalaryFundDeal.code == code) \
            .filter(SalaryFundDeal.trade_date == tradeDate) \
            .first()

    def getAllFundCodes(self):
        results = self.session.query(distinct(SalaryFundDeal.code)).all()
        codes = []
        for item in results:
            codes.append(item[0])
        return codes



if __name__ == "__main__":
    dao = SalaryFundDealDao()
    dao.getAllFundCodes()
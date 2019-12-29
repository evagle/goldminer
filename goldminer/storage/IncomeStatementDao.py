# coding: utf-8

from typing import List

from goldminer.models.models import IncomeStatement
from goldminer.storage.BaseDao import BaseDao


class IncomeStatementDao(BaseDao):

    def all(self) -> List[IncomeStatement]:
        return self.session.query(IncomeStatement).all()

    def getByCode(self, code) -> List[IncomeStatement]:
        return self.session.query(IncomeStatement) \
            .filter(IncomeStatement.code == code) \
            .order_by(IncomeStatement.end_date.desc()) \
            .all()

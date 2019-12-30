# coding: utf-8

from typing import List

from goldminer.models.models import CashflowStatement
from goldminer.storage.BaseDao import BaseDao


class CashflowStatementDao(BaseDao):

    def all(self) -> List[CashflowStatement]:
        return self.session.query(CashflowStatement).all()

    def getByCode(self, code) -> List[CashflowStatement]:
        return self.session.query(CashflowStatement) \
            .filter(CashflowStatement.code == code) \
            .order_by(CashflowStatement.end_date.desc()) \
            .all()

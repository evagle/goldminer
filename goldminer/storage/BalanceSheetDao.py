# coding: utf-8

from typing import List

from goldminer.models.models import BalanceSheet
from goldminer.storage.BaseDao import BaseDao


class BalanceSheetDao(BaseDao):

    def all(self) -> List[BalanceSheet]:
        return self.session.query(BalanceSheet).all()

    def getByCode(self, code) -> List[BalanceSheet]:
        return self.session.query(BalanceSheet) \
            .filter(BalanceSheet.code == code) \
            .order_by(BalanceSheet.end_date.desc()) \
            .all()

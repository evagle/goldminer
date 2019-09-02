# coding: utf-8

from typing import List

from goldminer.models.models import Indexes, DerivativeFinanceIndicator
from goldminer.storage.BaseDao import BaseDao


class DerivativeFinanceIndicatorDao(BaseDao):

    def all(self) -> List[DerivativeFinanceIndicator]:
        return self.session.query(DerivativeFinanceIndicator).all()

    def getByCode(self, code) -> List[DerivativeFinanceIndicator]:
        return self.session.query(DerivativeFinanceIndicator).filter(DerivativeFinanceIndicator.code == code)

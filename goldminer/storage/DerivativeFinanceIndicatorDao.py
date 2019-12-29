# coding: utf-8
import types
from typing import List

from goldminer.models.models import DerivativeFinanceIndicator
from goldminer.storage.BaseDao import BaseDao


class DerivativeFinanceIndicatorDao(BaseDao):

    def all(self) -> List[DerivativeFinanceIndicator]:
        return self.session.query(DerivativeFinanceIndicator).all()

    def getAllNPCUT(self):
        rows = self.session.query(DerivativeFinanceIndicator.code,
                                  DerivativeFinanceIndicator.pub_date,
                                  DerivativeFinanceIndicator.end_date,
                                  DerivativeFinanceIndicator.NPCUT).all()
        result = []
        for item in rows:
            obj = types.SimpleNamespace()
            obj.code = item[0]
            obj.pub_date = item[1]
            obj.end_date = item[2]
            obj.NPCUT = item[3]
            result.append(obj)
        return result

    def getAllROEAVG(self):
        rows = self.session.query(DerivativeFinanceIndicator.code,
                                  DerivativeFinanceIndicator.pub_date,
                                  DerivativeFinanceIndicator.end_date,
                                  DerivativeFinanceIndicator.ROEAVG).all()
        result = []
        for item in rows:
            obj = types.SimpleNamespace()
            obj.code = item[0]
            obj.pub_date = item[1]
            obj.end_date = item[2]
            obj.ROEAVG = item[3]
            result.append(obj)
        return result

    def getByCode(self, code) -> List[DerivativeFinanceIndicator]:
        return self.session.query(DerivativeFinanceIndicator) \
            .filter(DerivativeFinanceIndicator.code == code) \
            .order_by(DerivativeFinanceIndicator.end_date.desc()) \
            .all()

    def getFirstWithPubDateBefore(self, code, pub_date) -> DerivativeFinanceIndicator:
        return self.session.query(DerivativeFinanceIndicator) \
            .filter(DerivativeFinanceIndicator.code == code) \
            .filter(DerivativeFinanceIndicator.pub_date <= pub_date) \
            .order_by(DerivativeFinanceIndicator.pub_date.desc()) \
            .first()

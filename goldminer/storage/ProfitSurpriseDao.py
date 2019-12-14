# coding: utf-8

from typing import List

from goldminer.models.models import ProfitSurprise
from goldminer.storage.BaseDao import BaseDao


class ProfitSurpriseDao(BaseDao):

    def all(self) -> List[ProfitSurprise]:
        return self.session.query(ProfitSurprise).all()

    def getByCode(self, code) -> ProfitSurprise:
        return self.session.query(ProfitSurprise).filter(ProfitSurprise.code == code).all()

    def add(self, model: ProfitSurprise):
        self.session.add(model)
        self.session.commit()

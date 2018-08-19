# coding: utf-8

from typing import List

from models.models import IndexCorrelation
from storage.BaseDao import BaseDao


class IndexCorrelationDao(BaseDao):

    def all(self) -> List[IndexCorrelation]:
        return self.session.query(IndexCorrelation).all()

    def getByCode(self, codeA, codeB) -> IndexCorrelation:
        id = codeA + "_" + codeB
        return self.session.query(IndexCorrelation).\
            filter(IndexCorrelation.id == id).first()

    def add(self, model: IndexCorrelation):
        self.session.add(model)
        self.session.commit()


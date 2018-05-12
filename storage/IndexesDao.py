# coding: utf-8

from typing import List

from models.models import Indexes
from storage.BaseDao import BaseDao


class IndexesDao(BaseDao):

    def all(self) -> List[Indexes]:
        return self.session.query(Indexes).all()

    def getIndexList(self) -> List[str]:
        result = self.session.query(Indexes.code).all()
        return [i[0] for i in result]

    def add(self, index: Indexes):
        self.session.add(index)
        self.session.commit()

    def addAll(self, indexes):
        self.session.add_all(indexes)
        self.session.commit()

    def getIndexPublishDate(self, code: str):
        result = self.session.query(Indexes.pub_date).filter(Indexes.code == code).first()
        if result is not None:
            return result[0]
        return None

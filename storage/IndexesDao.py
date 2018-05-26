# coding: utf-8

from typing import List

from models.models import Indexes
from storage.BaseDao import BaseDao


class IndexesDao(BaseDao):

    def all(self) -> List[Indexes]:
        return self.session.query(Indexes).all()

    def getIndexList(self) -> List[str]:
        excludeIndexTypes = ["债券指数", "基金指数"]
        result = self.session.query(Indexes.code).filter(Indexes.index_type.notin_(excludeIndexTypes)).all()
        return [i[0] for i in result]

    def add(self, index: Indexes):
        self.session.add(index)
        self.session.commit()

    def getIndexPublishDate(self, code: str):
        result = self.session.query(Indexes.pub_date).filter(Indexes.code == code).first()
        if result is not None:
            return result[0]
        return None

dao = IndexesDao()
dao.getIndexList()
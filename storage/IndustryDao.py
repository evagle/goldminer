# coding: utf-8

from typing import List

from models.models import Industry
from storage.BaseDao import BaseDao


class IndustryDao(BaseDao):

    def all(self) -> List[Industry]:
        return self.session.query(Industry).all()

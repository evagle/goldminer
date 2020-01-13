# coding: utf-8

from typing import List

from goldminer.models.models import CnInfoOrgId
from goldminer.storage.BaseDao import BaseDao


class CnInfoOrgIdDao(BaseDao):

    def all(self) -> List[CnInfoOrgId]:
        return self.session.query(CnInfoOrgId).all()

    def getByCode(self, code) -> CnInfoOrgId:
        return self.session.query(CnInfoOrgId).filter(CnInfoOrgId.code == code).first()

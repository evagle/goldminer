# coding: utf-8

from typing import List

from goldminer.models.models import PerformancePreview
from goldminer.storage.BaseDao import BaseDao


class PerformancePreviewDao(BaseDao):

    def all(self) -> List[PerformancePreview]:
        return self.session.query(PerformancePreview).all()

    def getByCode(self, code) -> PerformancePreview:
        return self.session.query(PerformancePreview).filter(PerformancePreview.code == code).all()

    def add(self, model: PerformancePreview):
        self.session.add(model)
        self.session.commit()

    def getLatestPubDate(self):
        latest_pub_date = self.session.query(PerformancePreview.pub_date) \
            .order_by(PerformancePreview.pub_date.desc()) \
            .limit(1)

        return latest_pub_date

    def getFirstWithPubDateBefore(self, code, date) -> PerformancePreview:
        return self.session.query(PerformancePreview) \
            .filter(PerformancePreview.code == code) \
            .filter(PerformancePreview.pub_date <= date) \
            .order_by(PerformancePreview.pub_date.desc()) \
            .first()

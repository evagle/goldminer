# coding: utf-8

from typing import List

from goldminer.models.models import PerformanceForecast
from goldminer.storage.BaseDao import BaseDao


class PerformanceForecastDao(BaseDao):

    def all(self) -> List[PerformanceForecast]:
        return self.session.query(PerformanceForecast).all()

    def getByCode(self, code) -> PerformanceForecast:
        return self.session.query(PerformanceForecast).filter(PerformanceForecast.code == code).all()

    def add(self, model: PerformanceForecast):
        self.session.add(model)
        self.session.commit()

    def getLatestPubDate(self):
        latest_pub_date = self.session.query(PerformanceForecast.pub_date)\
                    .order_by(PerformanceForecast.pub_date.desc())\
                    .limit(1)

        return latest_pub_date

    def getFirstWithPubDateBefore(self, code, date) -> PerformanceForecast:
        return self.session.query(PerformanceForecast) \
            .filter(PerformanceForecast.code == code) \
            .filter(PerformanceForecast.pub_date <= date)\
            .order_by(PerformanceForecast.pub_date.desc()) \
            .first()


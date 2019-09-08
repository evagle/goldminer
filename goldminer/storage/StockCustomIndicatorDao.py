# coding: utf-8
from datetime import date
from typing import List

from sqlalchemy import Column

from goldminer.models.models import StockCustomIndicator
from goldminer.storage.BaseDao import BaseDao


class StockCustomIndicatorDao(BaseDao):

    def all(self) -> List[StockCustomIndicator]:
        return self.session.query(StockCustomIndicator).all()

    def getByDate(self, code, d: date) -> StockCustomIndicator:
        return self.session.query(StockCustomIndicator) \
            .filter(StockCustomIndicator.code == code) \
            .filter(StockCustomIndicator.trade_date == d) \
            .first()

    def getBatchByDate(self, codes: list, d: date) -> List[StockCustomIndicator]:
        if codes is None:
            return []
        bars = self.session.query(StockCustomIndicator) \
            .filter(StockCustomIndicator.trade_date == d) \
            .all()
        result = []
        for bar in bars:
            if bar.code in codes:
                result.append(bar)
        return result

    def getLatestDate(self, code=None, columnName=None):
        """
        Get latest Date where attr is not None
        :param columnName: column should not be none
        :return:
        """
        if columnName is None:
            raise Exception("columnName could not be None")
        if code is None:
            result = self.session.query(StockCustomIndicator.trade_date) \
                .filter(Column(columnName).isnot(None)) \
                .order_by(StockCustomIndicator.trade_date.desc()) \
                .first()
        else:
            result = self.session.query(StockCustomIndicator.trade_date) \
                .filter(Column(columnName).isnot(None)) \
                .filter(StockCustomIndicator.code == code) \
                .order_by(StockCustomIndicator.trade_date.desc()) \
                .first()
        return date(2005, 1, 1) if result is None else result[0]

    def getByCode(self, code):
        result = self.session.query(StockCustomIndicator) \
            .filter(StockCustomIndicator.code == code) \
            .order_by(StockCustomIndicator.trade_date.asc()) \
            .all()
        return result

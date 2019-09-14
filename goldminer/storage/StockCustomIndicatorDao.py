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

    def getAllAtDate(self, d: date):
        """
        Get all StockCustomIndicator bars for given date, return in dict
        {(code, trade_date): bar,...}
        :param d: date to retrieve
        :return:
        Dict:
        {(code, trade_date): bar,...}
        """
        bars = self.session.query(StockCustomIndicator) \
            .filter(StockCustomIndicator.trade_date == d) \
            .all()
        result = {}
        for bar in bars:
            result[(bar.code, bar.trade_date)] = bar
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

    def getByDateRange(self, code, startDate, endDate):
        query = self.session.query(StockCustomIndicator) \
            .filter(StockCustomIndicator.code == code)
        if startDate is not None:
            query = query.filter(StockCustomIndicator.trade_date >= startDate)
        if endDate is not None:
            query = query.filter(StockCustomIndicator.trade_date <= endDate)

        result = query.all()
        return result

    def getByCode(self, code):
        result = self.session.query(StockCustomIndicator) \
            .filter(StockCustomIndicator.code == code) \
            .order_by(StockCustomIndicator.trade_date.asc()) \
            .all()
        return result

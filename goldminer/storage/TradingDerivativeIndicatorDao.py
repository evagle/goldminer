# coding: utf-8
from typing import List

from goldminer.models.models import TradingDerivativeIndicator
from goldminer.storage.BaseDao import BaseDao


class TradingDerivativeIndicatorDao(BaseDao):
    def all(self) -> List[TradingDerivativeIndicator]:
        return self.session.query(TradingDerivativeIndicator).all()

    def getColumnValuesByDate(self, date, column):
        """
        获取在指定日期某个column的所有值
        :param code:
        :param column:
        :return: dict {code: column_value,...}
        """
        result = self.session.query(TradingDerivativeIndicator.code, column) \
            .filter(TradingDerivativeIndicator.pub_date == date) \
            .all()
        dic = {}
        for item in result:
            dic[item[0]] = item[1]
        return dic

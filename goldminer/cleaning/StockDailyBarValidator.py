# coding: utf-8
import math

from goldminer.common.logger import get_logger
from goldminer.spider.tushare.TSStockBarSpider import TSStockBarSpider
from goldminer.storage.StockDailyBarDao import StockDailyBarDao
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class StockDailyBarValidator:
    @staticmethod
    def check_abnormal_bar(code):
        """
        Find incorrect bar by compare
        :param code:
        :return:
        """
        stock_bar_dao = StockDailyBarDao()
        tushare_bar_spider = TSStockBarSpider()
        local_bars = stock_bar_dao.getByCode(code, adjust='none')
        ts_bars = tushare_bar_spider.download_bars_from_tushare(code, adj='none')
        ts_bars_dict = {}
        for bar in ts_bars:
            ts_bars_dict[(bar.code, bar.trade_date)] = bar

        abnormal_count = 0
        for bar in local_bars:
            key = (bar.code, bar.trade_date)
            if key not in ts_bars_dict:
                logger.info("key not exist in tushare: {}".format(key))
                continue
            obar = ts_bars_dict[key]
            if math.fabs(bar.close - obar.close) > 0.1:
                abnormal_count += 1
        if abnormal_count > 0:
            logger.error("code = {}, abnormal count = {}".format(code, abnormal_count))
        return abnormal_count


if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    for code in stocks:
        StockDailyBarValidator.check_abnormal_bar(code)

# coding: utf-8
from datetime import datetime, timedelta

from goldminer.common import GMConsts
from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.StockManager import StockManager
from goldminer.storage.StockCustomIndicatorDao import StockCustomIndicatorDao

logger = get_logger(__name__)


class RPSProcessor:
    def __init__(self):
        self.customIndicatorDao = StockCustomIndicatorDao()

    def process(self, trade_date):
        logger.info("Start processing rps for date {}".format(trade_date))

        bars = list(self.customIndicatorDao.getAllAtDate(trade_date).values())
        # 过滤掉B股
        left = []
        for bar in bars:
            if not bar.code.startswith("9"):
                left.append(bar)
        bars = left

        total_count = len(bars)
        MIN = -1e6

        has_rps = True
        for bar in bars:
            if bar.rps50 is None or bar.gain50 is None or bar.rps120 is None or bar.rps250 is None:
                has_rps = False

        if has_rps:
            logger.info("RPS had already been calculated for trade_date {}".format(trade_date))
            return None

        bars50 = sorted(bars, key=lambda bar: bar.gain50 if bar.gain50 is not None else MIN, reverse=True)
        for i in range(total_count):
            bar = bars50[i]
            if bar.gain50 is None:
                bar.rps50 = 0
            else:
                bar.rps50 = 100 - (i + 1) * 100 / total_count

        bars120 = sorted(bars, key=lambda bar: bar.gain120 if bar.gain120 is not None else MIN, reverse=True)
        for i in range(total_count):
            bar = bars120[i]
            if bar.gain120 is None:
                bar.rps120 = 0
            else:
                bar.rps120 = 100 - (i + 1) * 100 / total_count

        bars250 = sorted(bars, key=lambda bar: bar.gain250 if bar.gain250 is not None else MIN, reverse=True)
        for i in range(total_count):
            bar = bars250[i]
            if bar.gain250 is None:
                bar.rps250 = 0
            else:
                bar.rps250 = 100 - (i + 1) * 100 / total_count

        logger.info("{} rps bars updated".format(len(bars)))
        self.customIndicatorDao.bulkSave(bars)
        logger.info("End processing rps for date {}".format(trade_date))

    def getLastRPSDate(self):
        lastDate = GMConsts.TRADE_INIT_DATE
        lastDate = Utils.minDate(lastDate, self.customIndicatorDao.getLatestDate(code='000001', columnName='rps50'))
        return lastDate

    def buildAll(self):
        stockManager = StockManager()
        date = self.getLastRPSDate()
        endDate = datetime.today().date()
        logger.info("Start RPS processor from date {} to {}".format(date, endDate))
        while date <= endDate:
            if stockManager.isTradeDate(date):
                self.process(date)
            date = date + timedelta(days=1)

    def buildLastWeek(self):
        stockManager = StockManager()
        trade_dates = stockManager.getTradeDates()
        for d in trade_dates[-50:]:
            self.process(d)


if __name__ == "__main__":
    processor = RPSProcessor()
    processor.buildAll()

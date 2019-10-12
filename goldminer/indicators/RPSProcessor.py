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

    def hasRPS(self, bars):
        """
        Given a list of bars of one day,
        if 95% of the bars have rps, then we can think rps was already generated for that day,
        else the rps is not generated
        :param bars: all bars for one day
        :return: true if 95% bars have rps else false
        """
        if len(bars) == 0:
            return False

        n = 0
        for bar in bars:
            if bar.rps50 is not None and bar.rps120 is not None and bar.rps250 is not None:
                n += 1
        return n / len(bars) > 0.95

    def calculateRPS(self, bars, period):
        validBars = []
        rpsName = 'rps' + str(period)
        gainName = 'gain' + str(period)
        MIN = -1e6
        for bar in bars:
            if getattr(bar, gainName):
                validBars.append(bar)
            else:
                setattr(bar, rpsName, 0)

        if len(validBars) / len(bars) < 0.75:
            logger.warning("All bars have no enough(at least 75%) gain{} value".format(period))
            return False

        sortedBars = sorted(validBars,
                            key=lambda bar: getattr(bar, gainName) if getattr(bar, gainName) is not None else MIN,
                            reverse=True)
        count = len(sortedBars)

        for i in range(count):
            bar = sortedBars[i]
            rps = 100 - (i + 1) * 100 / count
            setattr(bar, rpsName, rps)

        logger.info("{} rps{} value updated".format(len(bars), period))
        return True

    def process(self, trade_date):
        logger.info("Start processing rps for date {}".format(trade_date))

        bars = list(self.customIndicatorDao.getAllAtDate(trade_date).values())

        if len(bars) == 0:
            logger.info("0 bars found at date: {}".format(trade_date))
            return None

        if self.hasRPS(bars):
            logger.info("RPS had already been calculated for trade_date {}".format(trade_date))
            return None

        updated = False
        for period in [50, 120, 250]:
            status = self.calculateRPS(bars, period)
            updated = updated or status

        if updated:
            self.customIndicatorDao.bulkSave(bars)
        logger.info("End processing rps for date {}".format(trade_date))

    def getLastRPSDate(self):
        lastDate = GMConsts.TRADE_INIT_DATE
        lastDate = Utils.maxDate(lastDate, self.customIndicatorDao.getLatestDate(code='000001', columnName='rps50'))
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

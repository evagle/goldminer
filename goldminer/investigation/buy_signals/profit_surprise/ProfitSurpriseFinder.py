# coding: utf-8
import datetime

from goldminer.common.Utils import Utils

from goldminer.common.logger import get_logger
from goldminer.models.models import ProfitSurprise
from goldminer.spider.tushare.TSStockBarSpider import TSStockBarSpider
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao

from goldminer.storage.PerformanceForecastDao import PerformanceForecastDao
from goldminer.storage.PerformancePreviewDao import PerformancePreviewDao
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDao import StockDao


class ProfitSurpriseFinder:
    def __init__(self):
        self.forecastDao = PerformanceForecastDao()
        self.previewDao = PerformancePreviewDao()
        self.stockBarDao = StockDailyBarAdjustNoneDao()
        self.derivativeFinanceIndicatorDao = DerivativeFinanceIndicatorDao()
        self.stockDao = StockDao()
        self.logger = get_logger(__name__)

    def find_forecast_before_date(self, code, date):
        """
        Find first forecast for stock with pub_date <= date
        :param code: stock symbol
        :param date: date to limit pub date
        :return: Forecast model
        """

        model = self.forecastDao.getFirstWithPubDateBefore(code, date)
        if model is None:
            return None

        if (date - model.pub_date).days > 8:
            return None

        return model

    def find_derivative_finance_indicator_before_date(self, code, date):
        model = self.derivativeFinanceIndicatorDao.getFirstWithPubDateBefore(code, date)
        if model is None:
            return None

        if (date - model.pub_date).days > 8:
            return None

        return model

    def find_preview_before_date(self, code, date):
        model = self.previewDao.getFirstWithPubDateBefore(code, date)
        if model is None:
            return None

        if (date - model.pub_date).days > 8:
            return None

        return model

    def findSurpurise(self, code):
        """
        找出因为业绩预告或者业绩快报或财报发布而产生的净利润断层
        :param code:
        :return:
        """
        bars = self.stockBarDao.getByCode(code)
        spider = TSStockBarSpider()
        bars = spider.getDailyBars(code)

        lastSurprise = None
        for i in range(len(bars) - 1):
            bar = bars[i]
            next_bar = bars[i + 1]
            # 如果跳空上涨4%以上，或者未跳空上涨9%
            if (next_bar.close > bar.close * 1.04 and next_bar.low > bar.high ) or \
                (next_bar.close > bar.close * 1.09):
                # 业绩预告
                performanceReports = {
                    "announcement": self.find_derivative_finance_indicator_before_date(code, next_bar.trade_date.date()),
                    "preview": self.find_preview_before_date(code, next_bar.trade_date.date()),
                    "forecast": self.find_forecast_before_date(code, next_bar.trade_date.date()),
                }

                for type, report in performanceReports.items():
                    if report:
                        if lastSurprise is not None and lastSurprise.pub_date == report.pub_date:
                            self.logger.info("Surprise exists")
                            continue
                        surprise = ProfitSurprise()
                        surprise.code = code
                        surprise.trade_date = next_bar.trade_date
                        surprise.pub_date = report.pub_date
                        surprise.type = type
                        if type == 'forecast':
                            surprise.profit_growth_low = report.growth_rate_low
                            surprise.profit_growth_high = report.growth_rate_high
                        elif type == 'preview':
                            surprise.profit_growth_low = report.profit_growth
                            surprise.profit_growth_high = report.profit_growth
                        elif type == 'announcement':
                            surprise.profit_growth_low = report.NPGRT
                            surprise.profit_growth_high = report.NPGRT
                        surprise.price_gap = 1 if next_bar.low > bar.high else 0
                        surprise.price_increase = Utils.formatFloat(next_bar.close * 100 / bar.close - 100, 3)
                        self.forecastDao.insertOrReplace(surprise)

                        self.logger.info("Find surprise code = {}, trade_date = {}, pub_date={}".format(
                            surprise.code, surprise.trade_date, surprise.pub_date))
                        lastSurprise = surprise


    def run(self):

        stocks = self.stockDao.getStockList()
        surprises = ['002791']
        for code in stocks:
            self.findSurpurise(code)



if __name__ == "__main__":
    profit = ProfitSurpriseFinder()
    profit.run()

    # For debugging
    surprises = [
        '002791',  # 坚郎五金，8.28 断层当天收绿，且只上涨0.78% 不考虑了 N

        '300319',  # 麦捷科技，10.14 Y
        '600183',  # 生益科技7月25 业绩快报 Y
        '000049',  # 德赛电池，724 业绩快报 Y
        '002045',  # 国光电器，715 Y
        '603008',  # 喜临门，724 断层当天收绿，业绩快报 Y
        '300413',  # 芒果超媒，8.30 断层当天收绿，且只上涨4% Y
        '300702',  # 天宇股份，8.22 断层当天收绿 Y
        '603936',  # 博敏电子，7.24 Y
        '002605',  # 姚记科技，10.15 Y
        '002850',  # 科达利，715 Y
        '600745',  # 闻泰科技，830 Y
        '002396',  # 星网锐捷，711 Y
        '002351',  # 漫步者，8.8 Y
        '603129',  # 春风动力，823 Y
        '002463',  # 沪电股份，626  Y
        '002705',  # 新宝股份，8.28 Y
        '300014',  # 亿纬锂能，10.8 Y
        '300558',  # 贝达药业，10.11 Y
        '300632',  # 光蒲股份，7.12 Y
        '300661',  # 圣邦股份，7.9 Y
        '603882',  # 金域医学，8.2 Y
        '603658',  # 安图生物，8.9 Y
        '300363',  # 博腾股份，7.31 Y
        '002124',  # 天邦股份，10.8 Y
        '002458',  # 益生股份，10.9 Y
    ]


# coding: utf-8
import math
from datetime import datetime

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.models.models import ProfitSurprise
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao
from goldminer.storage.PerformanceForecastDao import PerformanceForecastDao
from goldminer.storage.PerformancePreviewDao import PerformancePreviewDao
from goldminer.storage.StockDailyBarDao import StockDailyBarDao
from goldminer.storage.StockDao import StockDao


class ProfitSurpriseFinder:
    def __init__(self):
        self.forecastDao = PerformanceForecastDao()
        self.previewDao = PerformancePreviewDao()
        self.stockBarDao = StockDailyBarDao()
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

    def find_surprise(self, code, full=False):
        """
        找出因为业绩预告或者业绩快报或财报发布而产生的净利润断层
        :param full: 是否全量计算，如果是False则只计算半年内的数据
        :param code:
        :return:
        """
        if full:
            bars = self.stockBarDao.getByCode(code)
        else:
            bars = self.stockBarDao.getN(code, 120)
        # spider = TSStockBarSpider()
        # bars = spider.download_bars_from_tushare(code)

        last_surprise = None
        surprises = []
        for i in range(len(bars) - 1):
            bar = bars[i]
            next_bar = bars[i + 1]
            # 如果跳空上涨4%以上，或者未跳空上涨9%
            if (next_bar.close > bar.close * 1.04 and next_bar.low > bar.high) or \
                    (next_bar.close > bar.close * 1.09):
                # 业绩预告
                performanceReports = {
                    "announcement": self.find_derivative_finance_indicator_before_date(code,
                                                                                       next_bar.trade_date),
                    "preview": self.find_preview_before_date(code, next_bar.trade_date),
                    "forecast": self.find_forecast_before_date(code, next_bar.trade_date),
                }

                for type, report in performanceReports.items():
                    if report:
                        if last_surprise is not None and last_surprise.pub_date == report.pub_date:
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
                        last_surprise = surprise
                        surprises.append(surprise)
        return surprises

    def run(self):
        stocks = self.stockDao.getStockList()
        for code in stocks:
            self.find_surprise(code, full=False)


def gold_test():
    # For debugging
    expected_surprises = {
        # '002791',  # 坚郎五金，8.28 断层当天收绿，且只上涨0.78% 不考虑了 N

        '300319': datetime(2019, 10, 14).date(),  # 麦捷科技，10.14 Y
        '600183': datetime(2019, 7, 25).date(),  # 生益科技7月25 业绩快报 Y
        '000049': datetime(2019, 7, 24).date(),  # 德赛电池，724 业绩快报 Y
        '002045': datetime(2019, 7, 15).date(),  # 国光电器，715 Y
        '603008': datetime(2019, 7, 24).date(),  # 喜临门，724 断层当天收绿，业绩快报 Y
        '300413': datetime(2019, 8, 30).date(),  # 芒果超媒，8.30 断层当天收绿，且只上涨4% Y
        '300702': datetime(2019, 8, 22).date(),  # 天宇股份，8.22 断层当天收绿 Y
        '603936': datetime(2019, 7, 23).date(),  # 博敏电子，7.23 Y
        '002605': datetime(2019, 10, 15).date(),  # 姚记科技，10.15 Y
        '002850': datetime(2019, 7, 15).date(),  # 科达利，715 Y
        '600745': datetime(2019, 8, 30).date(),  # 闻泰科技，830 Y
        '002396': datetime(2019, 7, 11).date(),  # 星网锐捷，711 Y
        '002351': datetime(2019, 8, 8).date(),  # 漫步者，8.8 Y
        '603129': datetime(2019, 8, 23).date(),  # 春风动力，823 Y
        '002463': datetime(2019, 6, 26).date(),  # 沪电股份，626  Y
        '002705': datetime(2019, 8, 28).date(),  # 新宝股份，8.28 Y
        '300014': datetime(2019, 10, 8).date(),  # 亿纬锂能，10.8 Y
        '300558': datetime(2019, 10, 11).date(),  # 贝达药业，10.11 Y
        '300632': datetime(2019, 7, 12).date(),  # 光蒲股份，7.12 Y
        '300661': datetime(2019, 7, 9).date(),  # 圣邦股份，7.9 Y
        '603882': datetime(2019, 8, 2).date(),  # 金域医学，8.2 Y
        '603658': datetime(2019, 8, 9).date(),  # 安图生物，8.9 Y
        '300363': datetime(2019, 7, 31).date(),  # 博腾股份，7.31 Y
        '002124': datetime(2019, 10, 8).date(),  # 天邦股份，10.8 Y
        '002458': datetime(2019, 10, 9).date(),  # 益生股份，10.9 Y
    }

    for code in expected_surprises:
        surprises = profit.find_surprise(code)
        expected_date = expected_surprises[code]
        hit = False
        for surprise in surprises:
            if math.fabs((expected_date - surprise.trade_date).days) < 4:
                print("Hit code {} trade_date {}".format(code, expected_date))
                hit = True
        if not hit:
            print("Miss code {} trade_date {}".format(code, expected_date))


if __name__ == "__main__":
    profit = ProfitSurpriseFinder()
    profit.run()

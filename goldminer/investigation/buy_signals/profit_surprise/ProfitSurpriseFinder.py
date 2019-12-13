# coding: utf-8
import datetime

from goldminer.common.logger import get_logger
from goldminer.models.models import ProfitSurprise
from goldminer.spider.tushare.TSStockBarSpider import TSStockBarSpider
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao

from goldminer.storage.PerformanceForecastDao import PerformanceForecastDao
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDao import StockDao


class ProfitSurpriseFinder:
    def __init__(self):
        self.forecastDao = PerformanceForecastDao()
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

        if (date - model.pub_date).days > 7:
            return None

        return model

    def find_derivative_finance_indicator_before_date(self, code, date):
        model = self.derivativeFinanceIndicatorDao.getFirstWithPubDateBefore(code, date)
        if model is None:
            return None

        if (date - model.pub_date).days > 7:
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

            #####TODO DEBUG
            if bars[i].trade_date < datetime.datetime(2019,6,1):
                continue
            ###########

            bar = bars[i]
            next_bar = bars[i + 1]
            # 如果跳空上涨4%以上，或者未跳空上涨9%
            if (next_bar.close > bar.close * 1.04 and next_bar.low > bar.high ) or \
                (next_bar.close > bar.close * 1.09):
                # 业绩预告
                forecast = self.find_forecast_before_date(code, next_bar.trade_date.date())
                if forecast:
                    if lastSurprise is not None and lastSurprise.pub_date == forecast.pub_date:
                        self.logger.info("Surprise exists")
                        continue
                    surprise = ProfitSurprise()
                    surprise.code = code
                    surprise.trade_date = next_bar.trade_date
                    surprise.pub_date = forecast.pub_date
                    surprise.profit_growth_low = forecast.growth_rate_low
                    surprise.profit_growth_high = forecast.growth_rate_high
                    surprise.price_gap = 1 if next_bar.low > bar.high else 0
                    surprise.price_increase = next_bar.close / bar.close
                    # self.forecastDao.insertOrReplace(surprise)
                    print(surprise.code, surprise.trade_date, surprise.pub_date)
                    lastSurprise = surprise

                # TODO 业绩快报

                # 财报
                derivativeFinance = self.find_derivative_finance_indicator_before_date(code, next_bar.trade_date.date())
                print(code, next_bar.trade_date.date(), derivativeFinance)


                if derivativeFinance:
                    if lastSurprise is not None and lastSurprise.pub_date == derivativeFinance.pub_date:
                        self.logger.info("Surprise exists")
                        continue
                    surprise = ProfitSurprise()
                    surprise.code = code
                    surprise.trade_date = next_bar.trade_date
                    surprise.pub_date = derivativeFinance.pub_date
                    surprise.profit_growth_low = derivativeFinance.NPGRT
                    surprise.profit_growth_high = derivativeFinance.NPGRT
                    surprise.price_gap = 1 if next_bar.low > bar.high else 0
                    surprise.price_increase = next_bar.close / bar.close
                    # self.forecastDao.insertOrReplace(surprise)
                    print(surprise.code, surprise.trade_date, surprise.pub_date)
                    lastSurprise = surprise

    def run(self):

        stocks = [
            # '600183',  # 生益科技7月24 业绩快报
            # '000049',  # 德赛电池，724 业绩快报
            # '002045',  # 国光电器，715 业绩快报
            # '603008',  # 喜临门，724 断层当天收绿，业绩快报


            # '002791',  # 坚郎五金，8.28 断层当天收绿，且只上涨0.78% 不考虑了 N
            # '300319',  # 麦捷科技，10.14 业绩预告没下载下来

            # '300413',  # 芒果超媒，8.30 断层当天收绿，且只上涨4% Y
            # '300702',  # 天宇股份，8.22 断层当天收绿 Y
            # '603936',  # 博敏电子，7.24 Y
            # '002605',  # 姚记科技，10.15 Y
            # '002850',  # 科达利，715 Y
            # '600745',  # 闻泰科技，830 Y
            # '002396',  # 星网锐捷，711 Y
            # '002351',  # 漫步者，8.8 Y
            # '603129',  # 春风动力，823 Y
            # '002463',  # 沪电股份，626  Y
            # '002705',  # 新宝股份，8.28 Y
            # '300014',  # 亿纬锂能，10.8 Y
            # '300558',  # 贝达药业，10.11 Y
            # '300632',  # 光蒲股份，7.12 Y
            # '300661',  # 圣邦股份，7.9 Y
            # '603882',  # 金域医学，8.2 Y
            # '603658',  # 安图生物，8.9 Y
            # '300363',  # 博腾股份，7.31 Y
            # '002124',  # 天邦股份，10.8 Y
            # '002458',  # 益生股份，10.9 Y
            ]  # stockDao.getStockList()
        surprises = []
        for code in stocks:
            self.findSurpurise(code)



if __name__ == "__main__":
    profit = ProfitSurpriseFinder()
    profit.run()

# coding: utf-8
import datetime

from goldminer.spider.tushare.TSStockBarSpider import TSStockBarSpider

from goldminer.storage.PerformanceForecastDao import PerformanceForecastDao
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDao import StockDao


class ProfitSurprise:
    def find_forecast_before_date(self, code, date):
        """
        Find first forecast for stock with pub_date <= date
        :param code: stock symbol
        :param date: date to limit pub date
        :return: Forecast model
        """
        forecastDao = PerformanceForecastDao()
        forecast = forecastDao.getForecastBeforeDate(code, date)
        if (date - forecast.pub_date).days > 7:
            return None
        else:
            return forecast

    def run(self):
        stockDao = StockDao()
        stockBarDao = StockDailyBarAdjustNoneDao()
        stocks = ['300347']#stockDao.getStockList()
        for code in stocks:
            bars = stockBarDao.getByCode(code)
            spider = TSStockBarSpider()
            bars = spider.getDailyBars(code)
            # (C>=REF(CLOSE,1)*1.06)&&LOW>(REF(HIGH,1)+0.001)&&C>=O;
            for i in range(len(bars)-1):
                bar = bars[i]
                next_bar = bars[i+1]

                if next_bar.close > bar.close * 1.06 and next_bar.low > bar.high and next_bar.close > next_bar.open:
                    forecast = self.find_forecast_before_date(code, next_bar.trade_date.date())
                    if forecast:
                        print(code, next_bar.trade_date, forecast.pub_date, forecast.forecast_type)
                        print(forecast)
                        print("\n")



if __name__ == "__main__":
    profit = ProfitExceedExpectation()
    profit.run()
# coding: utf-8
import datetime
import json
import random
import time

import requests

from goldminer.common.logger import get_logger
from goldminer.models.models import PerformanceForecast
from goldminer.spider.eastmoney.EastMoneyBase import EastMoneyBase
from goldminer.storage.PerformanceForecastDao import PerformanceForecastDao


class PerformanceForecastSpider(EastMoneyBase):
    def __init__(self):
        super().__init__()
        self.__logger = get_logger(__name__)

        self.forecastDao = PerformanceForecastDao()

    def run(self):
        year = datetime.datetime.now().year
        # 业绩预告的开启时间
        forecast_window_config = [
            {
                "end_date": datetime.datetime(year - 1, 12, 31),
                "start": datetime.datetime(year - 1, 9, 30),
                "end": datetime.datetime(year, 1, 31)
            },
            {
                "end_date": datetime.datetime(year, 3, 31),
                "start": datetime.datetime(year, 1, 1),
                "end": datetime.datetime(year, 4, 15)
            },
            {
                "end_date": datetime.datetime(year, 6, 30),
                "start": datetime.datetime(year, 3, 31),
                "end": datetime.datetime(year, 7, 15)
            },
            {
                "end_date": datetime.datetime(year, 9, 30),
                "start": datetime.datetime(year, 6, 30),
                "end": datetime.datetime(year, 10, 15)
            },
            {
                "end_date": datetime.datetime(year, 12, 31),
                "start": datetime.datetime(year, 9, 30),
                "end": datetime.datetime(year + 1, 1, 31)
            },
        ]
        today = datetime.datetime.today()
        for window in forecast_window_config:
            # Give 15 more days for each window to accept forecast updates
            if window['start'] <= today <= window['end'] + datetime.timedelta(days=15):
                self.download_by_end_date(window['end_date'])

    def download_page(self, page, end_date, visited):
        enddate_str = end_date.strftime("%Y-%m-%d")
        params = {
            "type": "YJBB21_YJYG",
            "st": "ndate",
            "token": "70f12f2f4f091e459a279469fe49eca5",
            "sr": "-1",
            "p": str(page),
            "ps": "50",
            "filter": "(IsLatest='T')(enddate=^{}^)".format(enddate_str),
            "rt": "52521620",
            "js": "var rsDGWjfi={\"pages\":(tp),\"data\":(x),\"font\":(font)}"
        }

        return self.call_forecast_api(self._eastmoney_ajax_base_url, self._headers, params, visited)

    def make_forecast_model(self, item, font_mapping):
        """
        Accepting item and font_mapping, from eastmoney api, make a new PerformanceForecast model
        :param item:
        :param font_mapping:
        :return:
        """
        model = PerformanceForecast()
        for key in item:
            value = self.decode_numbers(item[key], font_mapping)
            if key == "scode":
                model.code = value
            elif key == "enddate":
                model.end_date = datetime.datetime.strptime(value[:10], "%Y-%m-%d").date()
            elif key == "ndate":
                model.pub_date = datetime.datetime.strptime(value[:10], "%Y-%m-%d").date()
            elif key == "forecasttype":
                model.forecast_type = value
            elif key == "forecastcontent":
                model.forecast_content = value
            elif key == "forecastl":
                model.profit_forecast_low = float(value)
            elif key == "forecastt":
                if value == "-":
                    model.profit_forecast_high = model.profit_forecast_low
                else:
                    model.profit_forecast_high = float(value)
            elif key == "yearearlier":
                if value == "-":
                    model.profit_last_year = 0
                else:
                    model.profit_last_year = float(value)
            elif key == "increasel":
                if value == "-":
                    model.growth_rate_low = 0
                else:
                    model.growth_rate_low = float(value)
            elif key == "increaset":
                if value == "-":
                    model.growth_rate_high = model.growth_rate_low
                else:
                    model.growth_rate_high = float(value)
            elif key == "changereasondscrpt":
                model.explanation = value
        return model

    def call_forecast_api(self, url, headers, params, visited):
        result = self.call_eastmoney_js_api(url, headers, params)
        if result is None:
            return None

        pages = result['pages']
        font_mapping = result['font']
        data = result['data']

        # total forecast count not be visited before
        total_count = 0
        new_count = 0
        for item in data:
            if item['forecastl'] == '-':
                self.__logger.warn("Skip data with forecastl = '-', data = {}".format(item))
                continue
            if item['scode'][:1] not in ['0', '3', '6']:
                self.__logger.warn("Skip scode {}, data = {}".format(item['scode'], item))
                continue

            model = self.make_forecast_model(item, font_mapping)

            key = (model.code, model.end_date, model.pub_date)
            if key in visited:
                self.__logger.info("Visited: {}".format(key))
                continue
            visited[key] = 1

            total_count += 1
            try:
                self.forecastDao.add(model)
                new_count += 1
            except Exception as e:
                self.__logger.warn("Failed to adding model, error message: {}".format(e))
                self.forecastDao.rollback()

        self.__logger.info(
            "Successfully download one page of performance forecast, forecast count={}".format(len(data)))
        time.sleep(random.randint(40, 100) / 50)

        self.__logger.info("New forecast count / total count(excludes visited) = {}/{}".format(new_count, total_count))
        if total_count > 0:
            new_forecast_ratio = new_count / total_count
        else:
            new_forecast_ratio = 1
        return pages, new_forecast_ratio


if __name__ == "__main__":
    spider = PerformanceForecastSpider()
    year = 2019
    spider.download_by_end_date(datetime.datetime(year, 9, 30))
    # spider.download_by_end_date(datetime.datetime(year, 9, 30))
    # spider.download_by_end_date(datetime.datetime(year, 6, 30))
    # spider.download_by_end_date(datetime.datetime(year, 3, 31))
    spider.run()

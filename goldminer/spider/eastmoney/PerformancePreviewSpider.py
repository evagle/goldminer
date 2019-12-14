# coding: utf-8
import datetime
import json
import random
import time

import requests

from goldminer.common.logger import get_logger
from goldminer.models.models import PerformancePreview
from goldminer.spider.eastmoney.EastMoneyBase import EastMoneyBase
from goldminer.storage.PerformancePreviewDao import PerformancePreviewDao


class PerformancePreviewSpider(EastMoneyBase):
    def __init__(self):
        super().__init__()
        self.__logger = get_logger(__name__)
        self.previewDao = PerformancePreviewDao()


    def run(self):
        year = datetime.datetime.now().year
        # 业绩预告的开启时间
        preview_window_config = [
            {
                "end_date": datetime.datetime(year - 1, 12, 31),
                "start": datetime.datetime(year - 1, 9, 30),
                "end": datetime.datetime(year, 4, 30)
            },
            {
                "end_date": datetime.datetime(year, 3, 31),
                "start": datetime.datetime(year, 1, 1),
                "end": datetime.datetime(year, 4, 30)
            },
            {
                "end_date": datetime.datetime(year, 6, 30),
                "start": datetime.datetime(year, 3, 31),
                "end": datetime.datetime(year, 8, 30)
            },
            {
                "end_date": datetime.datetime(year, 9, 30),
                "start": datetime.datetime(year, 6, 30),
                "end": datetime.datetime(year, 10, 31)
            },
            {
                "end_date": datetime.datetime(year, 12, 31),
                "start": datetime.datetime(year, 9, 30),
                "end": datetime.datetime(year + 1, 4, 30)
            },
        ]
        today = datetime.datetime.today()
        for window in preview_window_config:
            # Give 15 more days for each window to accept preview updates
            if window['start'] <= today <= window['end'] + datetime.timedelta(days=15):
                self.download_by_end_date(window['end_date'])

    def download_page(self, page, end_date, visited):
        enddate_str = end_date.strftime("%Y-%m-%d")
        params = {
            "type": "YJBB21_YJKB",
            "st": "ldate",
            "token": "70f12f2f4f091e459a279469fe49eca5",
            "sr": "-1",
            "p": str(page),
            "ps": "50",
            "filter": "(securitytypecode in ('058001001','058001002'))(rdate=^{}^)".format(enddate_str),
            "rt": "52541700",
            "js": "var eVCzgTPi={\"pages\":(tp),\"data\":(x),\"font\":(font)}"
        }
        return self.call_preview_api(self._eastmoney_ajax_base_url, self._headers, params, visited)

    def make_preview_model(self, item, font_mapping):
        """
        Accepting item and font_mapping, from eastmoney api, make a new Performancepreview model
        :param item:
        :param font_mapping:
        :return:
        """
        model = PerformancePreview()
        for key in item:
            value = self.decode_numbers(item[key], font_mapping)
            if value == "-":
                value = 0

            if key == "scode":
                model.code = value
            elif key == "rdate":
                model.end_date = datetime.datetime.strptime(value[:10], "%Y-%m-%d").date()
            elif key == "ldate":
                model.pub_date = datetime.datetime.strptime(value[:10], "%Y-%m-%d").date()
            elif key == "yysr":
                model.income = value
            elif key == "qntqys":
                model.income_previous = value
            elif key == "ys":
                model.income_growth = value
            elif key == "jlr":
                model.profit = float(value)
            elif key == "qntqjlr":
                model.profit_previous = float(value)
            elif key == "lr":
                model.profit_growth = float(value)
            elif key == "roeweighted":
                model.roe = float(value)
        return model

    def call_preview_api(self, url, headers, params, visited):
        result = self.call_eastmoney_js_api(url, headers, params)
        if result is None:
            return None

        pages = result['pages']
        font_mapping = result['font']
        data = result['data']

        # total preview count not be visited before
        total_count = 0
        new_count = 0
        for item in data:
            if item['scode'][:1] not in ['0', '3', '6']:
                self.__logger.warn("Skip scode {}, data = {}".format(item['scode'], item))
                continue

            model = self.make_preview_model(item, font_mapping)

            key = (model.code, model.end_date, model.pub_date)
            if key in visited:
                self.__logger.info("Visited: {}".format(key))
                continue
            visited[key] = 1

            total_count += 1
            try:
                self.previewDao.add(model)
                new_count += 1
            except Exception as e:
                self.__logger.warn("Failed to adding model, error message: {}".format(e))
                self.previewDao.rollback()

        self.__logger.info("Successfully download one page of performance preview, preview count={}".format(len(data)))
        time.sleep(random.randint(40, 100) / 50)

        self.__logger.info("New preview count / total count(excludes visited) = {}/{}".format(new_count, total_count))
        if total_count > 0:
            new_preview_ratio = new_count / total_count
        else:
            new_preview_ratio = 1
        return pages, new_preview_ratio


if __name__ == "__main__":
    spider = PerformancePreviewSpider()

    for year in range(2019, 2018, -1):
        spider.download_by_end_date(datetime.datetime(year, 3, 31))
        spider.download_by_end_date(datetime.datetime(year, 6, 30))
        spider.download_by_end_date(datetime.datetime(year, 9, 30))
        spider.download_by_end_date(datetime.datetime(year, 12, 31))
    # spider.run()

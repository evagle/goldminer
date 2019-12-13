# coding: utf-8
import datetime
import json
import random
import time

import requests

from goldminer.common.logger import get_logger
from goldminer.models.models import PerformancePreview
from goldminer.storage.PerformancePreviewDao import PerformancePreviewDao


class PerformancePreviewSpider():
    def __init__(self):
        self.__logger = get_logger(__name__)
        self.__headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh;q=0.6",
            "Host": "dcfm.eastmoney.com",
            "Referer": "http://data.eastmoney.com/bbsj/201803/yjyg.html",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        }
        self.__base_url = "http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get"

        self.previewDao = PerformancePreviewDao()

        self.__force_scan = False

    def set_force_scan(self, is_force = False):
        self.__force_scan = is_force

    def run(self):
        year = datetime.datetime.now().year
        # 业绩预告的开启时间
        preview_window_config = [
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
        for window in preview_window_config:
            # Give 15 more days for each window to accept preview updates
            if window['start'] <= today <= window['end'] + datetime.timedelta(days=15):
                self.download_by_end_date(window['end_date'])

    def download_by_end_date(self, end_date):
        if (end_date.month, end_date.day) not in [(3,31),(6,30),(9,30),(12,31),]:
            self.__logger.error("Wrong end date format: {}".format(end_date))
            return
        page = 1
        total_pages = 1
        self.__logger.info("Start downloading preview for end_date: {}".format(end_date))
        while page <= total_pages:
            result = self.download_page(page, end_date)
            if result is None:
                continue

            total_pages, new_preview_ratio = result
            self.__logger.info("Download page {}/{} successfully for end_date {}".format(page, total_pages, end_date))
            # stop if new preview ratio is less than 5 percent in current page,
            # which means > 95% previews in current page were in database already
            # if new_preview_ratio < 0.05:
            #     break
            page += 1

    def download_page(self, page, end_date):
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
        return self.call_eastmoney_preview_js_api(self.__base_url, self.__headers, params, {})

    def decode_numbers(self, string, font_mapping):
        for encoded_number in font_mapping:
            decoded_value = font_mapping[encoded_number]
            string = string.replace(encoded_number, decoded_value)
        return string

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

    def call_eastmoney_preview_js_api(self, url, headers, params, visited):
        """
        Call eastmoney api to get preview messages
        :param url:
        :param headers:
        :param params:
        :return:
        tuple (
            total pages,
            new preview ratio(=new count/total count)
        )
        """
        response = requests.get(url, params, headers=headers)
        if not response or not response.text:
            self.__logger.error("Failed to download data from url={}, params={}".format(url, params))
            return None

        content = response.text[13:]
        json_content = json.loads(content)


        font = json_content['font']
        font_mapping = {}
        if font is None or font['FontMapping'] is None:
            self.__logger.info("font is null for url={}, params={}".format(url, params))
            return None

        for item in font['FontMapping']:
            font_mapping[item['code']] = str(item['value'])

        data = json_content['data']
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
        return json_content['pages'], new_preview_ratio


if __name__ == "__main__":
    spider = PerformancePreviewSpider()

    for year in range(2019, 2009, -1):
        spider.download_by_end_date(datetime.datetime(year, 3, 31))
        spider.download_by_end_date(datetime.datetime(year, 6, 30))
        spider.download_by_end_date(datetime.datetime(year, 9, 30))
        spider.download_by_end_date(datetime.datetime(year, 12, 31))
    # spider.run()

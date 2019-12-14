# coding: utf-8
import json
from abc import abstractmethod

import requests

from goldminer.common.logger import get_logger


class EastMoneyBase:
    def __init__(self):
        self._headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh;q=0.6",
            "Host": "dcfm.eastmoney.com",
            "Referer": "http://data.eastmoney.com/bbsj/201803/yjyg.html",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        }
        self._eastmoney_ajax_base_url = "http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get"
        self._force_scan = False

        self.__logger = get_logger(__name__)

    def set_force_scan(self, is_force = False):
        self._force_scan = is_force

    def decode_numbers(self, string, font_mapping):
        for encoded_number in font_mapping:
            decoded_value = font_mapping[encoded_number]
            string = string.replace(encoded_number, decoded_value)
        return string

    def call_eastmoney_js_api(self, url, headers, params):
        """
        Call eastmoney api to get forecast messages
        :param url:
        :param headers:
        :param params:
        :return:
        tuple (
            total pages,
            new forecast ratio(=new count/total count)
        )
        """
        response = requests.get(url, params, headers=headers)
        if not response or not response.text:
            self.__logger.error("Failed to download data from url={}, params={}".format(url, params))
            return None

        content = response.text[13:]
        json_content = json.loads(content)

        font = json_content['font']
        if font is None or font['FontMapping'] is None:
            self.__logger.info("font is null for url={}, params={}".format(url, params))
            return None

        font_mapping = {}
        for item in font['FontMapping']:
            font_mapping[item['code']] = str(item['value'])

        json_content['font'] = font_mapping
        return json_content

    @abstractmethod
    def download_page(self, page, end_date, visited):
        pass

    def download_by_end_date(self, end_date):
        if (end_date.month, end_date.day) not in [(3, 31), (6, 30), (9, 30), (12, 31)]:
            self.__logger.error("Wrong end date format: {}".format(end_date))
            return

        page = 1
        total_pages = 1
        self.__logger.info("Start downloading forecast for end_date: {}".format(end_date))
        visited = {}

        # 当出现3个page的全部数据都在数据库中时，停止搜索
        break_condition = 3
        while page <= total_pages and break_condition > 0:
            result = self.download_page(page, end_date, visited)
            page += 1
            if result is None:
                continue

            total_pages, new_model_ratio = result
            # stop if new forecast ratio is less than 5 percent in current page,
            # which means > 95% forecasts in current page were in database already
            if new_model_ratio < 0.05:
                break_condition -= 1

            self.__logger.info("Download page {}/{} successfully for end_date {}".format(page, total_pages, end_date))

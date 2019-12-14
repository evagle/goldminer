# coding: utf-8
import json

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
        self._forcast_url = "http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get"
        self.__logger = get_logger(__name__)

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
        font_mapping = {}
        for item in font['FontMapping']:
            font_mapping[item['code']] = str(item['value'])

        json_content['font'] = font_mapping
        return json_content

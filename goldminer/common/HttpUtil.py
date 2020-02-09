# coding: utf-8
import os
from urllib import request

from fake_useragent import UserAgent


class HttpUtil:

    @staticmethod
    def get(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh;q=0.6"
        }
        req = request.Request(url, headers=headers)
        response = request.urlopen(req)
        return response.read()

    @staticmethod
    def random_user_agent():
        return UserAgent(cache=True,
                         use_cache_server=False,
                         path=os.getcwd() + "/fake-useragent.json").random

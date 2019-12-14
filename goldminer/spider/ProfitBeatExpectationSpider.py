# coding: utf-8
import random
import re
import time
import urllib.request


class ProfitBeatExpectationSpider:
    def __init__(self):
        pass

    def __findCode(self, text):
        searches = re.search(r"([630]0\d+)", text, re.M)
        if searches:
            return searches.group()

    def fromNxny(self):
        # si=5 最近半年，si=4 最近一个季度， si=3 最近一个月，si=2 最近一周
        baseUrl = "http://www.nxny.com/search_1.aspx?si=4&ft=2&fb=1&keyword=%s&page=%d"
        page = 1
        maxPage = 0
        codes = []
        while True:
            url = baseUrl % ("%u8D85%u9884%u671F", page)

            response = urllib.request.urlopen(url)
            content = response.read().decode('utf-8')

            # 匹配所有超预期个股信息
            results = re.findall(r"<a.*>(.*)</a>", content, re.M)
            for item in results:
                if "超预期" in item:
                    code = self.__findCode(item)
                    if code and code not in codes:
                        codes.append(code)
                    print(code)

            if maxPage == 0:
                searches = re.search(r"总页数:(\d+) 显示", content, re.M)
                if searches:
                    maxPage = int(searches.group(1))

            page += 1
            if page > maxPage:
                break
            else:
                time.sleep(random.randint(100, 2000) / 1000)

        print(codes)
        return codes


if __name__ == "__main__":
    spider = ProfitBeatExpectationSpider()
    spider.fromNxny()

# coding=utf-8

import json
import time
import urllib.request


## EastMoney's fund api:
# history: http://fund.eastmoney.com/pingzhongdata/512580.js
# lastday: http://fundgz.1234567.com.cn/js/512580.js


class EastMoney:

    def fetchFund(self, code):
        data = {}
        response = urllib.request.urlopen("http://fund.eastmoney.com/pingzhongdata/" + code + ".js")
        print("http://fund.eastmoney.com/pingzhongdata/" + code + ".js")
        html = response.read()
        if html is None or html == "":
            return {}

        html = html.decode('utf-8')
        lines = html.split(";")
        for line in lines:
            if line.find("var Data_netWorthTrend = ") > -1:
                pos = line.find("var Data_netWorthTrend = ") + 25
                history = line[pos:].replace(";", "")
                history = json.loads(history)
                for z in history:
                    record = {"code": code}
                    t = time.localtime(z["x"] / 1000)
                    date = "%d-%d-%d" % (t.tm_year, t.tm_mon, t.tm_mday)
                    record['trade_date'] = date
                    record['net'] = z["y"]
                    data[code + date] = record
            elif line.find("var Data_ACWorthTrend = ") > -1:
                pos = line.find("var Data_ACWorthTrend = ") + 24
                history = line[pos:].replace(";", "")
                history = json.loads(history)
                for z in history:
                    t = time.localtime(z[0] / 1000)
                    date = "%d-%d-%d" % (t.tm_year, t.tm_mon, t.tm_mday)
                    key = code + date
                    if key in data:
                        record = data[key]
                        record["acc"] = z[1]
        data = list(data.values())
        for i in range(1, len(data)):
            data[i]["change"] = 100 * (data[i]['net'] - data[i - 1]['net']) / data[i - 1]['net'];
        return data

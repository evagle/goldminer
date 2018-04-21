# coding=utf-8
import MySQLdb
import codecs
from datetime import *
import time
import urllib
import json

import sys
sys.path.append('../')
from DB import *

## EastMoney's fund api:
# history: http://fund.eastmoney.com/pingzhongdata/512580.js
# lastday: http://fundgz.1234567.com.cn/js/512580.js

class EastMoney:
    def __init__(self):
        self.db = DB()
    
    def fundHistory(self, code):
        data = {}
        response = urllib.request.urlopen("http://fund.eastmoney.com/pingzhongdata/"+code+".js") 
        html = response.read()
        if html is None or html == "":
            return {}

        html = html.decode('utf-8')
        lines = html.split("\r\n")
        for line in lines:
            if line.startswith("var Data_netWorthTrend = "):
                history = line.replace("var Data_netWorthTrend = ", "").replace(";", "");
                history = json.loads(history)
                for z in history:
                    record = {"code":code}
                    t = time.localtime(z["x"]/1000)
                    date = "%d-%d-%d" % (t.tm_year,t.tm_mon, t.tm_mday)
                    record['trade_date'] = date
                    record['net'] = z["y"]
                    data[code+date] = record
            elif line.startswith("var Data_ACWorthTrend = "):
                history = line.replace("var Data_ACWorthTrend = ", "").replace(";", "");
                history = json.loads(history)
                for z in history:
                    t = time.localtime(z[0]/1000)
                    date = "%d-%d-%d" % (t.tm_year,t.tm_mon, t.tm_mday)
                    key = code+date
                    if key in data:
                        record = data[key]
                        record["acc"] = z[1]
        data = list(data.values())
        for i in range(1, len(data)):
            data[i]["change"] = 100*(data[i]['net'] - data[i-1]['net'])/data[i-1]['net']; 
        return data    
        


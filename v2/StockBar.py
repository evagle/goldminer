
# coding: utf-8

# In[3]:


from gmsdk.api import StrategyBase
from gmsdk import md
import MySQLdb
import codecs
from datetime import *
import time

class DateUtil():
    @staticmethod
    def toMysqlDatetimeStr(strtime):
        date = datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S+08:00")
        return date.strftime("%Y-%m-%d %H:%M:%S")
    
class DB():
    def __init__(self):
        self.db = MySQLdb.connect("unionfight.citypet.cn","pocketpet","3MjdvUuXqxca6cbc","goldminer",charset="utf8")
        self.cursor = self.db.cursor()
    
    def addStockDailyBar(self, bar):
        sql = """INSERT INTO bar_daily_adjust_none(code, trade_date, open, close, high, low, amount, volume, 
        adj_factor, pre_close, upper_limit, lower_limit)
         VALUES ('%s', '%s', %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)"""
        sql = sql % (bar.sec_id, DateUtil.toMysqlDatetimeStr(bar.strtime), bar.open, bar.close, bar.high, bar.low, 
                     bar.amount, bar.volume, bar.adj_factor, bar.pre_close, bar.upper_limit, bar.lower_limit)
#         print(sql)
        self.cursor.execute(sql)
        self.db.commit()
        
    def getStockList(self):
        sql = "select code from stocks"
        self.cursor.execute(sql)
        self.db.commit()
        results = self.cursor.fetchall()
        stocks = []
        for row in results:
            stocks.append(row[0])
        return stocks
        
    def getStockStartDate(self, code):
        sql = "select pub_date from stocks where code = '%s'" % code
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchone()[0]
    
    def getStockLatestDate(self, code):
        sql = "select trade_date from bar_daily_adjust_none where code = '%s' order by trade_date desc limit 1" % code
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result is None:
            return None
        return result[0]
        
class StockData():
    def __init__(self):
        self.db = DB()
        
    def getStockList(self):
        return self.db.getStockList()
    
    def getSymbol(self, code):
        if code[0:1] == "6":
            return "SHSE"
        return "SZSE"
    
    def queryAllStockBar(self, md, code):
        startdate = self.db.getStockLatestDate(code)
        if startdate is None:
            startdate = self.db.getStockStartDate(code)
        else:
            startdate = startdate + timedelta(days=1)
        enddate = datetime.now()+timedelta(days=1)
        print(startdate, enddate)
        bars = md.get_dailybars(self.getSymbol(code) + "." + code, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
        return bars
    
    def saveBars(self, bars):
        for bar in bars:
            self.db.addStockDailyBar(bar)
        print("insert %d bars" % len(bars))

ret = md.init("17611258516", "web4217121")
stockData = StockData()
for code in stockData.getStockList():
    print("##", code, "##")
    bars = stockData.queryAllStockBar(md, code)
    stockData.saveBars(bars)
    time.sleep(0.1)
# print(stockData.getStockList())

# ticks = md.get_dailybars("SZSE.000001", "2015-10-29", "2015-12-29")
# db = DB()
# for tick in ticks:
#     print(tick.bar_type, tick.adj_factor, tick.amount, tick.volume, tick.open, tick.close, tick.high, tick.low, tick.lower_limit, tick.upper_limit,
#          tick.exchange, tick.flag, tick.pre_close, tick.sec_id, tick.lower_limit, tick.upper_limit)
#     db.addStockDailyBar(tick)
#     break
# print(dir(ticks[0]))


# In[ ]:


if __name__ == '__main____':
    ret = MyStrategy(
        username='17611258516',
        password='web4217121',
        strategy_id='9c8a4a49-3359-11e8-8fda-001c42a1c0e2',
        subscribe_symbols='SHSE.600000.tick',
        mode=2
        ).run()
    print(('exit code: ', ret))


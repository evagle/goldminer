# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

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

    def executeSql(self, sql):
        print(sql)
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()
    
    def addStockDailyBar(self, bar):
        sql = """INSERT IGNORE INTO bar_daily_adjust_none(code, trade_date, open, close, high, low, amount, volume, 
        adj_factor, pre_close, upper_limit, lower_limit)
         VALUES ('%s', '%s', %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)"""
        sql = sql % (bar.sec_id, DateUtil.toMysqlDatetimeStr(bar.strtime), bar.open, bar.close, bar.high, bar.low, 
                     bar.amount, bar.volume, bar.adj_factor, bar.pre_close, bar.upper_limit, bar.lower_limit)
#         print(sql)
        insertcount self.cursor.execute(sql)
        self.db.commit()
        return insertcount
    
    def fundamentalToSql(self, code, fundamental, fieldstr):
        sql = "('%s', '%s' , '%s'" % (code, fundamental['pub_date'], fundamental['end_date'])
        
        fields = fieldstr.split(",")
        
        for field in fields:
            if field in fundamental:
                sql += (", %lf" % fundamental[field])
            else:
                sql += ", 0"

        sql = sql + ")"
        # print(sql)
        return sql
        
    def addFundamental(self, code, fundamentals, table, fieldstr):
        fields = fieldstr.split(",")
        sql = "INSERT IGNORE INTO "+table+"(code, pub_date, end_date,"  + fieldstr + ") VALUES "
        
        for fundamental in fundamentals:
            sql += self.fundamentalToSql(code, fundamental, fieldstr) + ","
        sql = sql[:-1] + ";"

        # print(sql)
        insertcount = self.cursor.execute(sql)
        self.db.commit()
        return insertcount
        
    def addIndexConstituent(self, code, constituent):
        sql = """INSERT IGNORE INTO index_constituents(code, trade_date, constituents) VALUES ('%s', '%s', "%s")"""
        sql = sql % (code, constituent['trade_date'], constituent['constituents'])
        insertcount = self.cursor.execute(sql)
        self.db.commit()
        return insertcount

    def getStockList(self):
        sql = "select code from stocks"
        self.cursor.execute(sql)
        self.db.commit()
        results = self.cursor.fetchall()
        stocks = []
        for row in results:
            stocks.append(row[0])
        return stocks

    def getIndexList(self):
        sql = "select code from indexes"
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

    def getLastIndexDate(self, code):
        sql = "select trade_date from index_constituents where code = '%s' order by trade_date desc limit 1" % code
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result is None:
            return datetime(2005, 1, 1)
        return result[0]
 
    def getLastFundamentalsDate(self, code, table):
        sql = "select pub_date from %s where code = '%s' order by pub_date desc limit 1" % (table, code)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result is None:
            return datetime(2005, 1, 1)
        return result[0] + timedelta(days=1)


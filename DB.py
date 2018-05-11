# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

import MySQLdb
import codecs
from datetime import *
import time
from models.models import *

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqldb://pocketpet:3MjdvUuXqxca6cbc@unionfight.citypet.cn:3306/goldminer?charset=utf8')
Base = declarative_base()

class DateUtil():
    @staticmethod
    def toMysqlDatetimeStr(strtime):
        date = datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S+08:00")
        return date.strftime("%Y-%m-%d %H:%M:%S")
    
class DB():
    def __init__(self):
        self.db = MySQLdb.connect("unionfight.citypet.cn","pocketpet","3MjdvUuXqxca6cbc","goldminer",charset="utf8")
        self.cursor = self.db.cursor()
        
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
    
    def getStockList(self):
        result = self.session.query(Stocks.code).all()
        return [i[0] for i in result]
    
    def getIndexList(self):
        result = self.session.query(Indexes.code).all()
        return [i[0] for i in result]
        
    def executeSql(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()
    
    def addStockDailyBar(self, bar):
        sql = """INSERT IGNORE INTO bar_daily_adjust_none(code, trade_date, open, close, high, low, amount, volume, 
        adj_factor, pre_close, upper_limit, lower_limit)
         VALUES ('%s', '%s', %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)"""
        sql = sql % (bar.sec_id, DateUtil.toMysqlDatetimeStr(bar.strtime), bar.open, bar.close, bar.high, bar.low, 
                     bar.amount, bar.volume, bar.adj_factor, bar.pre_close, bar.upper_limit, bar.lower_limit)
        insertcount = self.cursor.execute(sql)
        self.db.commit()
        return insertcount

    ###############
    ## Insert index bar
    ###############
    def indexBarToSql(self, bar):
        sql = "('%s', '%s' , %f, %f, %f, %f, %f, %f, %f)"
        if 'pre_close' not in bar:
            bar.pre_close = 0
        if 'amount' not in bar:
            print(bar)
            bar.amount = 0
        if 'open' not in bar:
            print(bar)
            bar.open = 0
        if 'high' not in bar:
            print(bar)
            bar.high = 0
        if 'low' not in bar:
            print(bar)
            bar.low = 0
        sql = sql % (bar.symbol[5:], bar.bob.strftime("%Y-%m-%d"), bar.open, bar.close, bar.high, bar.low, 
                     bar.amount, bar.volume, bar.pre_close)
        return sql

    def addIndexDailyBar(self, bars):
        sql = """INSERT IGNORE INTO index_bar_daily(code, trade_date, open, close, high, low, amount, volume, pre_close)
         VALUES """

        for bar in bars:
            sql += self.indexBarToSql(bar) + ","
        sql = sql[:-1] + ";"

        insertcount = self.cursor.execute(sql)
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
        constituent['constituents'] = constituent['constituents'].replace("'", "\"")
        sql = """INSERT IGNORE INTO index_constituents(code, trade_date, constituents) VALUES ('%s', '%s', '%s')"""
        sql = sql % (code, constituent['trade_date'], constituent['constituents'])
        insertcount = self.cursor.execute(sql)
        self.db.commit()
        return insertcount

    
    def getStockStartDate(self, code):
        result = self.session.query(Stocks.pub_date).filter(Stocks.code == code)\
                     .order_by(Stocks.pub_date.desc()).first()
        return result[0]
    
    def getStockLatestDate(self, code):
        result = self.session.query(BarDailyAdjustNone.trade_date)\
                     .filter(BarDailyAdjustNone.code == code)\
                     .order_by(BarDailyAdjustNone.trade_date.desc()).first()
                     
        return datetime(2001, 1, 1) if result is None else result[0]

    def getIndexBarLatestDate(self, code):
        result = self.session.query(IndexBarDaily.trade_date)\
                     .filter(IndexBarDaily.code == code)\
                     .order_by(IndexBarDaily.trade_date.desc()).first()
                     
        return datetime(2001, 1, 1) if result is None else result[0]
    
    def getIndexConstituentsLatestDate(self, code):
        result = self.session.query(IndexConstituents.trade_date)\
                     .filter(IndexConstituents.code == code)\
                     .order_by(IndexConstituents.trade_date.desc()).first()
                     
        return datetime(2001, 1, 1) if result is None else result[0]

    def getFundamentalsLatestDate(self, table, code):
        result = self.session.query(table.trade_date)\
                     .filter(table.code == code)\
                     .order_by(table.trade_date.desc()).first()
                     
        return datetime(2001, 1, 1) if result is None else result[0]

  
 
    def getLastFundamentalsDate(self, code, table):
        sql = "select pub_date from %s where code = '%s' order by pub_date desc limit 1" % (table, code)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result is None:
            return datetime(2001, 1, 1)
        return result[0] + timedelta(days=1)

db = DB()
print(db.getIndexConstituentsLatestDate('00000x'))
print(db.getIndexBarLatestDate('000001'))
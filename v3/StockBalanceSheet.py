
# coding: utf-8

# In[ ]:


# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import sys
import MySQLdb
import codecs
from datetime import *
import time

sys.path.append('../')
from DB import *


set_token('a0998908534d317105b2184afbe436a4104dc51b')

class DateUtil():
    @staticmethod
    def toMysqlDatetimeStr(strtime):
        date = datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S+08:00")
        return date.strftime("%Y-%m-%d %H:%M:%S")
    
# class DB():
#     def __init__(self):
#         self.db = MySQLdb.connect("unionfight.citypet.cn","pocketpet","3MjdvUuXqxca6cbc","goldminer",charset="utf8")
#         self.cursor = self.db.cursor()
    
#     def addStockDailyBar(self, bar):
#         sql = """INSERT INTO bar_daily_adjust_none(code, trade_date, open, close, high, low, amount, volume, 
#         adj_factor, pre_close, upper_limit, lower_limit)
#          VALUES ('%s', '%s', %f, %f, %f, %f, %f, %f, %f, %f, %f, %f)"""
#         sql = sql % (bar.sec_id, DateUtil.toMysqlDatetimeStr(bar.strtime), bar.open, bar.close, bar.high, bar.low, 
#                      bar.amount, bar.volume, bar.adj_factor, bar.pre_close, bar.upper_limit, bar.lower_limit)
#         self.cursor.execute(sql)
#         self.db.commit()

#     def addIndexConstituent(self, code, constituent):
#         sql = """INSERT INTO index_constituents(code, trade_date, constituents) VALUES ('%s', '%s', "%s")"""
#         print(constituent.keys())
#         sql = sql % (code, constituent['trade_date'], constituent['constituents'])
#         self.cursor.execute(sql)
#         self.db.commit()
    
#     def fundamentalToSql(self, code, fundamental, fieldstr):
#         sql = "('%s', '%s' , '%s'" % (code, fundamental['pub_date'], fundamental['end_date'])
        
#         fields = fieldstr.split(",")
        
#         for field in fields:
#             if field in fundamental:
#                 sql += (", %lf" % fundamental[field])
#             else:
#                 sql += ", 0"

#         sql = sql + ")"
#         # print(sql)
#         return sql
        
#     def addFundamental(self, code, fundamentals, table, fieldstr):
#         fields = fieldstr.split(",")
#         sql = "INSERT INTO "+table+"(code, pub_date, end_date,"  + fieldstr + ") VALUES "
        
#         for fundamental in fundamentals:
#             sql += self.fundamentalToSql(code, fundamental, fieldstr) + ","
        
#         sql = sql[:-1] + ";"

#         # print(sql)
#         self.cursor.execute(sql)
#         self.db.commit()

#     def getStockList(self):
#         sql = "select code from stocks"
#         self.cursor.execute(sql)
#         self.db.commit()
#         results = self.cursor.fetchall()
#         stocks = []
#         for row in results:
#             stocks.append(row[0])
#         return stocks

#     def getIndexList(self):
#         sql = "select code from indexes"
#         self.cursor.execute(sql)
#         self.db.commit()
#         results = self.cursor.fetchall()
#         stocks = []
#         for row in results:
#             stocks.append(row[0])
#         return stocks
        
#     def getStockStartDate(self, code):
#         sql = "select pub_date from stocks where code = '%s'" % code
#         self.cursor.execute(sql)
#         self.db.commit()
#         return self.cursor.fetchone()[0]
    
#     def getStockLatestDate(self, code):
#         sql = "select trade_date from bar_daily_adjust_none where code = '%s' order by trade_date desc limit 1" % code
#         self.cursor.execute(sql)
#         result = self.cursor.fetchone()
#         if result is None:
#             return None
#         return result[0]

#     def getLastIndexDate(self, code):
#         sql = "select trade_date from index_constituents where code = '%s' order by trade_date desc limit 1" % code
#         self.cursor.execute(sql)
#         result = self.cursor.fetchone()
#         if result is None:
#             return datetime(2005, 1, 1)
#         return result[0] + timedelta(days=1)

#     def getLastFundamentalsDate(self, code, table):
#         sql = "select pub_date from %s where code = '%s' order by pub_date desc limit 1" % (table, code)
#         self.cursor.execute(sql)
#         result = self.cursor.fetchone()
#         if result is None:
#             return datetime(2005, 1, 1)
#         return result[0] + timedelta(days=1)

        
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

class FundamentalsData():
    def __init__(self):
        self.db = DB()

    def getSymbol(self, code):
        if code[0:1] == "6":
            return "SHSE"
        return "SZSE"

    def getFundamentals(self, code, table, fieldstr):
        startdate = self.db.getLastFundamentalsDate(code, table)
        enddate = datetime.now()+timedelta(days=1)
        print(startdate, enddate, self.getSymbol(code)+ "." +code)
        results = get_fundamentals(table=table, symbols=self.getSymbol(code) + "." + code, 
            start_date=startdate, end_date=enddate, limit=10000,
                fields=fieldstr)
        return results
    def removeDuplicate(self, fundamentals):
        results = {}
        for fundamental in fundamentals:
            key = fundamental['symbol'] + fundamental['pub_date'].strftime("%Y-%m-%d") + fundamental['end_date'].strftime("%Y-%m-%d")
            if key in results and not self.isSame(fundamental, results[key]):
                print("*****", fundamental, results[key])
            else:
                results[key] = fundamental
        return results.values()
    def isSame(self, item1, item2):
        keys = item1.keys()

        for key in keys:
            if key not in item2 or item1[key] != item2[key]:
                return False
        return True
    def saveFundamentals(self, code, fundamentals, table, fieldstr):
#         for fundamental in fundamentals:
        fundamentals = self.removeDuplicate(fundamentals)
        if len(fundamentals) > 0:
            self.db.addFundamental(code, fundamentals, table, fieldstr)
            print("insert %d fundamentals" % len(fundamentals))
        else:
            print("%s is up to date" % code)


fieldstr = 'ACCHELDFORS,ACCOPAYA,ACCORECE,ACCREXPE,ACCUDEPR,ACTITRADSECU,ACTIUNDESECU,ADVAPAYM,AVAISELLASSE,BDSPAYA,BDSPAYAPERBOND,BDSPAYAPREST,CAPISURP,CENBANKBORR,COMASSE,CONSPROG,COPEPOUN,COPEWITHREINRECE,COPEWORKERSAL,CURFDS,CURTRANDIFF,DEFEINCOTAXLIAB,DEFEREVE,DEFETAXASSET,DEPOSIT,DERIFINAASSET,DERILIAB,DEVEEXPE,DIVIDRECE,DIVIPAYA,DOMETICKSETT,DUENONCLIAB,ENGIMATE,EQUIINVE,EXPECURRLIAB,EXPENONCLIAB,EXPINONCURRASSET,EXPOTAXREBARECE,FDSBORR,FIXEDASSECLEA,FIXEDASSEIMMO,FIXEDASSEIMPA,FIXEDASSENET,FIXEDASSENETW,GENERISKRESE,GOODWILL,HOLDINVEDUE,HYDRASSET,INSUCONTRESE,INTAASSET,INTELPAY,INTELRECE,INTEPAYA,INTERECE,INTETICKSETT,INVE,INVEPROP,LCOPEWORKERSAL,LENDANDLOAN,LIABHELDFORS,LOGPREPEXPE,LONGBORR,LONGDEFEINCO,LONGPAYA,LONGRECE,MARGRECE,MARGREQU,MINYSHARRIGH,NOTESPAYA,NOTESRECE,OCL,OTHEQUIN,OTHERCURRASSE,OTHERCURRELIABI,OTHERFEEPAYA,OTHERLONGINVE,OTHERNONCASSE,OTHERNONCLIABI,OTHERPAY,OTHERRECE,PAIDINCAPI,PARESHARRIGH,PERBOND,PLAC,PREMRECE,PREP,PREPEXPE,PREST,PRODASSE,PUBLISHDATE,PURCRESAASSET,REINCONTRESE,REINRECE,RESE,RIGHAGGR,SELLREPASSE,SETTRESEDEPO,SFORMATCURRASSE,SFORMATCURRELIABI,SFORMATNONCASSE,SFORMATNONCLIAB,SFORMATPARESHARRIGH,SFORMATRIGHAGGR,SFORMATTOTASSET,SFORMATTOTLIAB,SFORMATTOTLIABSHAREQUI,SHORTTERMBDSPAYA,SHORTTERMBORR,SMERGERCURRASSE,SMERGERCURRELIABI,SMERGERNONCASSE,SMERGERNONCLIAB,SMERGERPARESHARRIGH,SMERGERRIGHAGGR,SMERGERTOTASSET,SMERGERTOTLIAB,SMERGERTOTLIABSHAREQUI,SPECPAYA,SPECRESE,SUBSRECE,SUNEVENASSETLIABEUQI,SUNEVENCURRASSE,SUNEVENCURRELIABI,SUNEVENNONCASSE,SUNEVENNONCLIAB,SUNEVENPARESHARRIGH,SUNEVENRIGHAGGR,SUNEVENTOTASSET,SUNEVENTOTLIAB,SUNEVENTOTLIABSHAREQUI,TAXESPAYA,TOPAYCASHDIVI,TOTALCURRLIAB,TOTALNONCASSETS,TOTALNONCLIAB,TOTASSET,TOTCURRASSET,TOTLIAB,TOTLIABSHAREQUI,TRADFINASSET,TRADFINLIAB,TRADSHARTRAD,TREASTK,UNDIPROF,UNREINVELOSS,UNSEG,WARLIABRESE'
table = 'balance_sheet'
providor = FundamentalsData()
stockData = StockData()
for code in stockData.getStockList():
    print("##", code, "##")

    fundamentals = providor.getFundamentals(code, table, fieldstr)
    providor.saveFundamentals(code, fundamentals, table, fieldstr)


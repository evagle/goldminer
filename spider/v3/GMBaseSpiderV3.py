# coding: utf-8
from datetime import date

from gm.api import *

from common.GMConsts import ADJUST_NONE


class GMBaseSpiderV3:
    def __init__(self):
        set_serv_addr("140.143.64.121:7001")
        set_token('a0998908534d317105b2184afbe436a4104dc51b')

    def currentTick(self, symbols, fields=''):
        return current(symbols, fields)

    # Support both stock and index, distinguish by symbol
    def getHistory(self, symbol, frequency, start_time, end_time, fields=None, skip_suspended=True,
                fill_missing=None, adjust=ADJUST_NONE, adjust_end_time='', df=False):
        return history(symbol, frequency, start_time, end_time, fields, skip_suspended, \
                       fill_missing, adjust, adjust_end_time, df)

    def getHistoryN(self, symbol, frequency, count, end_time=None, fields=None, skip_suspended=True,
          fill_missing=None, adjust=ADJUST_NONE, adjust_end_time='', df=False):
        return history_n(symbol, frequency, count, end_time, field, skip_suspended, \
                         fill_missing, adjust, adjust_end_time, df)

    def getFundamentals(self, table, symbols, start_date, end_date, fields=None, filter=None, order_by=None, limit=1000, df=False):
        return get_fundamentals(table, symbols, start_date, end_date, fields, filter, order_by, limit, df)

    def getFundamentalsN(table, symbols, end_date, fields=None, filter=None, order_by=None, count=1, df=False):
        return get_fundamentals_n(table, symbols, end_date, fields, filter, order_by, count, df)


    def getInstruments(self, symbols=None, exchanges=None, sec_types=None, names=None, skip_suspended=True, \
                       skip_st=True, fields=None, df=False):
        return get_instruments(symbols, exchanges, sec_types, names, skip_suspended, skip_st, fields, df)

    def getHistoryInstruments(self, symbols, fields=None, start_date=None, end_date=None, df=False):
        return get_history_instruments(symbols, fields, start_date, end_date, df)

    def getInstrumentinfos(self, symbols=None, exchanges=None, sec_types=None, names=None, fields=None, df=False):
        return get_instrumentinfos(symbols, exchanges, sec_types, names, fields, df)

    def getHistoryConstituents(self, index, start_date=None, end_date=None):
        return get_history_constituents(index, start_date, end_date)

    def getConstituents(self, index, fields=None, df=False):
        return get_constituents(index, fields, df)

    def getIndustry(self, code):
        return get_industry(code)

    def getTradingDates(self, exchange, start_date, end_date):
        return get_trading_dates(exchange, start_date, end_date)

    def getPreviousTradingDate(self, exchange, date):
        return get_previous_trading_date(exchange, date)

    def getNextTradingDate(self, exchange, date):
        return get_next_trading_date(exchange, date)

    def getDividend(self, symbol, start_date, end_date=None):
        return get_dividend(symbol, start_date, end_date)

    def _rawDataToModel(self, code: str, raw: dict, modelClass):
        model = modelClass()
        for key in raw:
            val = raw[key]
            if hasattr(model, key):
                if key in ["trade_date", "pub_date", "end_date"] and type(val) == date:
                    setattr(model, key, val.date())
                else:
                    setattr(model, key, val)
        return model

    def getIndexSymbol(self, code):
        if code[0:1] == "0":
            return "SHSE"
        return "SZSE"

    def codeToIndexSymbol(self, code):
        return self.getIndexSymbol(code) + "." + code

    def getStockSymbol(self, code):
        if code[0:1] == "6" or code[0:1] == "9":
            return "SHSE"
        return "SZSE"

    def codeToStockSymbol(self, code):
        return self.getStockSymbol(code) + "." + code

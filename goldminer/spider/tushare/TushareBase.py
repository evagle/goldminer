# coding: utf-8

import tushare as ts


class TushareBase:
    def __init__(self):
        self.ts_pro_api = ts.pro_api('707e43764dbbf6de8eb6a077ee68fa977b4190c014d5ce3ce74e3dc7')

    def to_ts_code(self, code):
        if code[0:1] == "6":
            ts_code = code + ".SH"
        else:
            ts_code = code + ".SZ"
        return ts_code

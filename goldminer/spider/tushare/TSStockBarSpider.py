# coding: utf-8
from datetime import datetime

from goldminer.models.models import StockDailyBarAdjustNone
from goldminer.spider.tushare.TushareBase import TushareBase

import tushare as ts


class TSStockBarSpider(TushareBase):

    def getDailyBars(self, code, adj='qfq', start_date: datetime=None, end_date: datetime=None):
        if start_date is None:
            start_date = datetime(2001, 1, 1).strftime("%Y%m%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        ts_code = self.to_ts_code(code)
        df = ts.pro_bar(pro_api=self.ts_pro_api, ts_code=ts_code, adj=adj, start_date=start_date, end_date=end_date)

        bars = []
        for row in df.itertuples(index=False):
            bar = StockDailyBarAdjustNone()
            bar.code = code
            bar.trade_date = datetime.strptime(row.trade_date, "%Y%m%d")
            bar.open = row.open
            bar.close = row.close
            bar.high = row.high
            bar.low = row.low
            bar.pre_close = row.pre_close
            bar.amount = row.amount
            bar.volume = row.vol
            bars.append(bar)

        bars = sorted(bars, key=lambda bar: bar.trade_date, reverse=False)
        return bars


if __name__ == "__main__":
    spider = TSStockBarSpider()
    bars = spider.getDailyBars('000001')
    print(bars)
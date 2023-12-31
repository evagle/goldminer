# coding: utf-8
from datetime import datetime

import tushare as ts

from goldminer.common.Utils import Utils
from goldminer.models.models import StockDailyBar
from goldminer.spider.tushare.TushareBase import TushareBase


class TSStockBarSpider(TushareBase):
    def __init__(self):
        super().__init__()

    def download_bars_from_tushare(self, code, start_date: datetime = None, end_date: datetime = None, adj='qfq'):
        if start_date is None:
            start_date = datetime(2005, 1, 1).strftime("%Y%m%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        ts_code = self.to_ts_code(code)

        df = ts.pro_bar(api=self.ts_pro_api, ts_code=ts_code, adj=adj, start_date=start_date, end_date=end_date,
                        adjfactor=True)

        if df is None:
            return None

        bars = []
        for row in df.itertuples(index=False):
            bar = StockDailyBar()
            bar.code = code
            bar.trade_date = datetime.strptime(row.trade_date, "%Y%m%d").date()
            attrs = ['open', 'close', 'high', 'low', 'pre_close']
            for attr in attrs:
                if adj == 'hfq':
                    value = getattr(row, attr) / row.adj_factor
                    setattr(bar, attr, Utils.formatFloat(value, 2))
                else:
                    setattr(bar, attr, getattr(row, attr))

            bar.amount = row.amount
            bar.volume = row.vol
            bar.adj_factor = row.adj_factor

            bars.append(bar)

        bars = sorted(bars, key=lambda bar: bar.trade_date, reverse=False)
        return bars


if __name__ == "__main__":
    spider = TSStockBarSpider()
    bars_qfq = spider.download_bars_from_tushare('000001', adj='none')


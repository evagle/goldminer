# coding: utf-8
from goldminer.indicators.StockManager import StockManager
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao


class RPSProcessor:
    def __init__(self):
        self.stockBarPrevDao = StockDailyBarAdjustPrevDao()

    def process(self, trade_date):
        bars = self.stockBarPrevDao.getByDate(trade_date)
        # 过滤掉B股
        filtered = []
        for bar in bars:
            if not bar.code.startswith("9"):
                filtered.append(bar)
        bars = filtered

        total_count = len(bars)
        MIN = -1e6

        has_rps = True
        for bar in bars:
            if bar.rps50 is None or bar.rps50 is None or bar.rps50 is None:
                has_rps = False

        if has_rps:
            print("rps already calculated for trade_date", trade_date)
            return None

        bars50 = sorted(bars, key=lambda bar: bar.gain50 if bar.gain50 is not None else MIN, reverse=True)
        for i in range(total_count):
            bar = bars50[i]
            if bar.gain50 is None:
                bar.rps50 = 0
            else:
                bar.rps50 = 100 - (i + 1) * 100 / total_count

        bars120 = sorted(bars, key=lambda bar: bar.gain120 if bar.gain120 is not None else MIN, reverse=True)
        for i in range(total_count):
            bar = bars120[i]
            if bar.gain120 is None:
                bar.rps120 = 0
            else:
                bar.rps120 = 100 - (i + 1) * 100 / total_count

        bars250 = sorted(bars, key=lambda bar: bar.gain250 if bar.gain250 is not None else MIN, reverse=True)
        for i in range(total_count):
            bar = bars250[i]
            if bar.gain250 is None:
                bar.rps250 = 0
            else:
                bar.rps250 = 100 - (i + 1) * 100 / total_count

        print(len(bars), "updated")
        self.stockBarPrevDao.bulkSave(bars)

    def build(self):
        stockManager = StockManager()
        trade_dates = stockManager.getTradeDates()
        for d in trade_dates:
            print("start", d)
            self.process(d)
            print("end", d)


if __name__ == "__main__":
    processor = RPSProcessor()
    processor.build()

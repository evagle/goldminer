# coding: utf-8
from goldminer.common import GMConsts
from goldminer.storage.IndexDailyBarDao import IndexDailyBarDao
from goldminer.storage.IndexesDao import IndexesDao


class IndexRanker:
    def __init__(self):
        self.indexBarDao = IndexDailyBarDao()
        self.indexesDao = IndexesDao()

    def ndayGain(self, bars, n):
        changedBars = []
        for i in range(n, len(bars)):
            attr = "gain" + str(n)

            # close可能等于零，此时找后面的几个bar
            close = 0
            for j in range(10):
                close = bars[i - n + j].close
                if close > 0:
                    break
                else:
                    print("Error bar close = 0", bars[i - n + j])

            val = (bars[i].close - close) / close * 100 if close > 0 else 0
            setattr(bars[i], attr, val)
            changedBars.append(bars[i])

        # print(len(changedBars), "bars updated")
        return bars

    def rank(self, codes):
        barsList = []
        for code in codes:
            barsList.append(self.indexBarDao.getByCode(code))

        barsGroupByTradeDate = {}
        for bars in barsList:
            for n in [30, 50, 120, 250]:
                self.ndayGain(bars, n)
            for bar in bars:
                datestr = bar.trade_date.strftime("%Y%m%d")
                if datestr not in barsGroupByTradeDate:
                    barsGroupByTradeDate[datestr] = []
                barsGroupByTradeDate[datestr].append(bar)

        for date in barsGroupByTradeDate:
            bars = barsGroupByTradeDate[date]

            for n in [30, 50, 120, 250]:
                attr = "gain" + str(n)
                sortedBars = sorted(bars, key=lambda bar: getattr(bar, attr) if hasattr(bar, attr) else GMConsts.MIN_GAIN, reverse=True)
                rankattr = "rank" + str(n)
                for i in range(len(sortedBars)):
                    setattr(sortedBars[i], rankattr, i+1)

        return sorted(barsGroupByTradeDate.items(), key=lambda d: d, reverse=False)


'''
1. 排在第一的说明近期强度最高，在指数中期信号到来时买入最强指数总是一个不错的选择
2. 第一名常客：中证消费，证券公司，中证军工，创业板指等
3. 当第一名易主超过两天或者第一名，需要考虑换仓
4. 衍生策略：买入第一的指数etf，当发生以下情况换仓
    a) 当前持仓跌破仓位，或者接近亏损
    b) 第一名直接掉到第3名或以后
    c) 新第一名确立（新第一名待稳两天）
'''
if __name__ == "__main__":

    # 大盘指数
    marketIndex = ['000001', '399001', '399106', '399005', '399006', '000016', '000300', '000905', '000852', '000003',
                   '399101', '399102', '399318']

    # 重要细分指数
    industryIndex = ['399975', '000991', '000827', '000932', '399971', '000015', '000922', '399812', '000993', '399967']

    # 中证行业指数
    zzIndustry = ["000998", "399997", "000929", "000980", "399971", "000953", "000936", "000930", "000937", "399813",
                  "000955", "000922", "000827", "000934", "399987", "399967", "000931", "000960", "399998", "000938",
                  "000928", "000985", "000961", "399804", "000932", "399808", "000964", "000935", "000926", "399989",
                  "000933", "399986", "000832"]

    all = marketIndex + industryIndex
    codes = all

    ranker = IndexRanker()
    barsGroup = ranker.rank(codes)

    indexesDao = IndexesDao()
    indexes = {}
    for code in codes:
        indexes[code] = indexesDao.getByCode(code)

    n = 50
    attr = "gain" + str(n)
    for tradeDate, bars in barsGroup:
        s = tradeDate
        bars = sorted(bars, key=lambda bar: getattr(bar, attr) if hasattr(bar, attr) else GMConsts.MIN_GAIN, reverse=True)
        for b in bars:
            if hasattr(b, attr):
                # print(tradeDate, b.code, indexes[b.code].name, b.gain50)
                s += "\t" + indexes[b.code].name + "\t" + str(getattr(b, attr))
        print(s)


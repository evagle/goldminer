# coding: utf-8
from enum import Enum


class ProfileMetric(Enum):
    GrossProfitMargin = "毛利率"  # 毛利率
    NetProfitMargin = "净利率"  # 净利率
    ThreeFeeRatio = "三费"  # 三费占比
    SalesRatio = "销售"
    ManagementRatio = "管理"
    FinanceRatio = "财务"
    ROIC = "ROIC"  # 投入资本回报率
    ROE = "ROE"  # 净资产回报率
    ROA = "ROA"  # 总资产回报率
    IncomeGrowth = "营收增速"  # 营收增速
    NetProfitGrowth = "净利润增速"  # 净利润增速
    NetProfitCutGrowth = "扣非增速"  # 扣非净利润增速
    BIZCashFlow = "经营现金流"  # 经营活动产生现金流量净额 BIZNETCFLOW
    FreeCashFlow = "自由现金流"  # 自由现金流
    InventoryTurnoverRate = "存货周转率"  # 存货周转率/次
    TotalAssetTurnoverRate = "总资产周转率"  # 总资产周转率/次
    AccountReceivableTurnoverRate = "应收周转率"  # 应收账款周转率/次
    AssetLiabilityRatio = "资产负债率"  # 资产负债率
    CurrentRatio = "流动比率"  # 流动比率
    QuickRatio = "速动比率"  # 速动比率
    EquityMultiplier = "权益乘数"  # 权益乘数=总资产/股东权益(净资产)
    AccountPayable = "应付"
    AccountReceivable = "应收"
    AdvancePayment = "预收"
    Prepaid = "预付"
    Upstream = "上游"
    Downstream = "下游"
    Occupation = "总占款"
    ProfitCashRatio = "净现比"
    NetProfit = "净利润"

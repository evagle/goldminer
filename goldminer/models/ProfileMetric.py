# coding: utf-8
from enum import Enum


class ProfileMetric(Enum):
    GrossProfitMargin = "毛利率"  # 毛利率=（主营业务收入-主营业务成本）/主营业务收入×100%
    NetProfitMargin = "净利率"  # 净利率=[净利润/（营业收入+营业外收入）]×100%
    ThreeFeeRatio = "三费费用"  # 三费占比
    SalesRatio = "销售费用"
    ManagementRatio = "管理费用"
    FinanceRatio = "财务费用"
    RDExpenseRatio = "研发费用"
    ROIC = "ROIC"  # 投入资本回报率
    ROE = "ROE"  # 净资产回报率
    ROA = "ROA"  # 总资产回报率
    IncomeGrowth = "营收增速"  # 营收增速
    NetProfitGrowth = "净利润增速"  # 净利润增速
    NetProfitCutGrowth = "扣非增速"  # 扣非净利润增速
    BIZCashFlow = "经营现金流"  # 经营活动产生现金流量净额 BIZNETCFLOW
    InvestCashFlow = "投资现金流"  # 投资活动产生现金流量净额 INVNETCASHFLOW
    FinancialCashFlow = "筹资现金流"  # 筹资活动产生现金流量净额 FINNETCFLOW
    FreeCashFlow = "自由现金流"  # 自由现金流
    InventoryTurnoverRate = "存货周转率"  # 存货周转率/次
    TotalAssetTurnoverRate = "总资产周转率"  # 总资产周转率/次
    AccountReceivableTurnoverRate = "应收周转率"  # 应收账款周转率/次=销售收入/平均应收账款
    AssetLiabilityRatio = "资产负债率"  # 资产负债率=总负债/总资产
    InterestLiabilityRatio = "有息负债率"  # 有息负债率=有息负债/总资产
    CurrentRatio = "流动比率"  # 流动比率
    QuickRatio = "速动比率"  # 速动比率
    InterestLiabilityCoverage = "有息覆盖率"  # 有息负债覆盖率=（货币资金）/ 有息负债
    EquityMultiplier = "权益乘数"  # 权益乘数=总资产/股东权益(净资产)
    AccountPayable = "应付"
    AccountReceivable = "应收"  # 应收票据+应收账款+应收股利+应收出口退税+应收利息+其他应收款+应收保费+应收分保合同准备金+应收分保账款
    AccountReceivableRatio = "应收占比"  # 应收占比=应收/总资产
    AdvancePayment = "预收"
    Prepaid = "预付"
    Upstream = "上游"
    Downstream = "下游"
    Occupation = "总占款"
    ProfitCashRate = "净现比"
    NetProfit = "净利润"
    NetProfitCut = "扣非净利润"
    CoreProfit = "核心利润"  # 核心利润 = 毛利润-三费-税金及附加=（主营）营业收入-营业成本-三费-税金及附加
    CoreProfitMargin = "核心利润率"  # 核心利润率 = 核心利润/营业收入
    CoreProfitGrowth = "核心增长率"  # 核心利润增长率

    # 核心利润比 = 核心利润/营业利润，越大说明运营利润的贡献占比越高。
    # 营业利润 = 营业总收入-营业总支出+公允价值变动收益+投资收益+汇兑收益+资产处置收益+其他收益
    # 与核心利润相比，营业利润多了后面几项与经营无关的收益即：公允价值变动收益+投资收益+汇兑收益+资产处置收益+其他收益
    CoreProfitRate = "核心利润比"
    CapitalExp = "资本开支"  # Capital Expenditures = 购建固定资产、无形资产和其他长期资产所支付的现金
    SalesRevenueRate = "销售收现率"  # = 销售商品提供劳务收到的现金/营业收入
    GoodwillRate = "商誉占比"  # = 商誉/净资产
    OtherReceivableRatio = "其他应收比"  # 其他应收款占总资产比 = 其他应收款余额÷总资产×100 %, 大于10%就很危险
    OtherPayRatio = "其他应付比"  # 其他应付款占总资产比 = 其他应付款余额÷总资产×100 %, 优秀的公司接近0
    MonetaryFundsRatio = "货币资金比"  # 货币资金占比=货币资金/总资产
    # 经营性资产占比=（应收xx+长期应收+存货）/总资产
    OperatingAssetRatio = "经营资产占比"
    ProductAssetRatio = "生产资产占比"  # 生产性资产占比=生产性资产/总资产
    # 投资资产占比=投资资产(=交易性金融资产+持有至到期投资+可供出售金融资产+买入返售金融资产
    # +长期股权投资+投资性房地产)/总资产
    InvestmentAssetRatio = "投资资产占比"  # (交易性金融资产+持有至到期投资+可供出售金融资产+买入返售金融资产+长期股权投资+投资性房地产)/总资产
    OtherAssetRatio = "其他资产占比"  # 其他资产占比=(其他流动资产+其他非流动资产)/总资产

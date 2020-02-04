# coding: utf-8
from datetime import date
from enum import Enum

import pandas as pd

from goldminer.common.Utils import Utils
from goldminer.storage.BalanceSheetDao import BalanceSheetDao
from goldminer.storage.CashflowStatementDao import CashflowStatementDao
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao
from goldminer.storage.IncomeStatementDao import IncomeStatementDao


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
    ProfitCashRatio = "净现比"
    NetProfit = "净利润"



class StockProfile:
    def __init__(self):
        self.derivative_dao = DerivativeFinanceIndicatorDao()
        self.income_dao = IncomeStatementDao()
        self.balance_sheet_dao = BalanceSheetDao()
        self.cashflow_dao = CashflowStatementDao()

    def _add_metric_to_profile(self, profile: dict, end_date: date, metric: ProfileMetric, value):
        if end_date not in profile:
            profile[end_date] = {}
        profile[end_date][metric.value] = value
        return profile

    def _calc_npcut_growth(self, derivative_models):
        dic = {}
        for model in derivative_models:
            key = (model.end_date.year, model.end_date.month)
            dic[key] = model

        for model in derivative_models:
            model.NPCUTGRT = 0
            pre_key = (model.end_date.year - 1, model.end_date.month)
            if pre_key in dic:
                pre_model = dic[pre_key]
                if pre_model.NPCUT != 0:
                    model.NPCUTGRT = (model.NPCUT - pre_model.NPCUT) / pre_model.NPCUT * 100

        return derivative_models

    def make_profile(self, code):
        """
        ## 护城河分析
        护城河就是竞争优势，可以从两个方向看：1 是否比别人卖的贵 2 是否比别人成本低

        卖的贵可以量化成毛利率高，成本低量化为三费（销售+管理+财务）低
        * 毛利率（DerivativeFinanceIndicator.SGPMARGIN）
            * 转换成本
            * 无形资产
                * 品牌
                * 专利
                * 垄断
            * 网络效应
        * 三费占比（（销售费用+管理费用+财务费用）/营业收入）（IncomeStatement，自己算）
            * 地理位置
            * 规模
            * 独特资源或技术
            * 优化流程
        * ROIC 资本回报率（DerivativeFinanceIndicator）
            * 如果能做到长期平均ROIC > 15%, 就表示公司极大可能有护城河


        ## 盈利能力分析
        1. 毛利率=（营业收入-营业成本）/营业收入（DerivativeFinanceIndicator）
            * 衡量是否比别人卖的贵
            * 更适用传统重资产公司
        2. 净利率=净利润/营业收入=（营业收入-营业成本-三费）/营业收入（DerivativeFinanceIndicator）
            * 和毛利率比减了三费
            * 适用于轻资产公司，营业成本低但是三费高
        3. roe净资产收益率=净利润/净资产（股东权益）（DerivativeFinanceIndicator，ROEAVG不扣非, ROEAVGCUT扣非）
            * 去除规模影响，可以跨行业比较
            * 代表没一元钱股东权益能赚多少钱
        4. roa总资产收益率（DerivativeFinanceIndicator）
            * 对于高负债（高杠杆）公司，股东权益低导致roe很高，因为用借的钱来赚钱，这时roa就更好反应公司盈利能力

        ## 成长能力分析
        看4个关键指标
        1. 营业总收入增长率（DerivativeFinanceIndicator，TAGTH）
            * 营收增长越快说明公司越赚钱，再对比同行业其他公司就能知道市场份额是否在不断扩大
            * 营收增速看公司所处成长周期
                * >10%成长期
                * 5%-10%成熟期
                * <5%衰退期
            * 单纯营收增速快不代表成长好（例如靠烧钱扩张来的），长期稳定的营业收入增长带来长期稳定的净利润增长才是企业核心竞争力，是成长能力的体现
        2. 净利润/扣非净利润增速（DerivativeFinanceIndicator，NPGTH，扣非需要自己算）
            * 希望看到的是净利润增速比营收增速更高，说明可以在不增加等比例成本的情况下赚更多的钱
            * 排雷：需要排除通过增大应收账款和存货来虚增净利润的造假行为
        3. 经营活动现金流增速（经营活动现金流与净利润的关系）（IncomeStatement自己算）
            * 经营活动现金流量是指企业投资活动和筹资活动以外的所有的交易和事项产生的现金流量。它是企业现金的主要来源。
            * 净现比=经营活动现金流/净利润, 净现比1左右比较好
            * 经营活动现金流量的净流入持续增长说明公司有价值
        4. 自由现金流=经营活动现金流-资本开支（IncomeStatement自己算）
            * 自由现金流才是真金白银的收入，它不断增长才表示公司成长能力优秀
            * 资本开支：这部分支出在现金流量表中体现在“购建固定资产、无形资产和其他长期资产所支付的现金”项目

        ## 运营能力分析
        4个关键指标
        1. 存货周转率=营业成本/平均存货（DerivativeFinanceIndicator，INVTURNRT）
            * 存货周转率越高表示营业周期越短，流动性越强，反应存货管理水平，简单说就是卖货非常快。
            * 平均存货=期初和期末存货的均值
        2. 总资产周转率=营业收入/总资产平均余额（DerivativeFinanceIndicator）
            * 数值越大表示周转越快，说明销售能力越强
            * 衡量企业运用资产赚取利润的能力
        3. 应收账款周转率=营业收入/平均应收账款余额（DerivativeFinanceIndicator）
            * 数值越大说明资金回收越快，应收占营收的比例越小，反之就需要考虑应收账款变坏账问题了
            * 需要分行业区分对待，在行业内比较
        4. 三费占比（DerivativeFinanceIndicator自己算）
            * 三费占比低其实也是运营能力强的表现，说明成本控制的好

        ## 偿债能力分析
        偿债能力是指企业用其资产偿还长期债务与短期债务的能力。
        1. 资产负债率=总负债/总资产（DerivativeFinanceIndicator）
            * 总负债占总资产比例，超过50%就可能发生资不抵债了
            * 具体值要行业内比较，银行地产都是传统的高负债行业
        2. 流动比率=流动资产/流动负债（DerivativeFinanceIndicator）
            * 衡量短期债务清偿能力，数值高代表偿债能力越好
            * 因为流动资产包括了应收账款和存货，所以太大了也可能有问题
            * 一般维持2左右比较好
        3. 速动比率=速动资产/流动负债（DerivativeFinanceIndicator）
            * 速动资产等于流动资产减存货等不容易变现的资产。表示短期负债能够快速用变现资产的方式偿还
            * 比例维持1左右比较好，具体行业具体分析，零售业基本都小于1

        :return: 个股Profile最新季度的数据加上所有年度数据按时间降序
        """
        profile = {}

        models = self.derivative_dao.getByCode(code)
        models = self._calc_npcut_growth(models)
        selected = self._filter_annual_and_latest(models)

        for model in selected:
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.ROIC, Utils.formatFloat(model.ROIC, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.ROE,
                                        Utils.formatFloat(model.ROEAVGCUT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.ROA, Utils.formatFloat(model.ROA, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.NetProfitMargin,
                                        Utils.formatFloat(model.SNPMARGINCONMS, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.IncomeGrowth,
                                        Utils.formatFloat(model.TAGRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.NetProfitGrowth,
                                        Utils.formatFloat(model.NPGRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.NetProfitCutGrowth,
                                        Utils.formatFloat(model.NPCUTGRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.InventoryTurnoverRate,
                                        Utils.formatFloat(model.INVTURNRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.TotalAssetTurnoverRate,
                                        Utils.formatFloat(model.TATURNRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AccountReceivableTurnoverRate,
                                        Utils.formatFloat(model.ACCRECGTURNRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AssetLiabilityRatio,
                                        Utils.formatFloat(model.ASSLIABRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.CurrentRatio,
                                        Utils.formatFloat(model.CURRENTRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.QuickRatio,
                                        Utils.formatFloat(model.QUICKRT, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.FreeCashFlow,
                                        Utils.formatFloat(model.FCFF / 10000, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.EquityMultiplier,
                                        Utils.formatFloat(model.EM, 2))

        # 利润表数据
        models = self.income_dao.getByCode(code)
        selected = self._filter_annual_and_latest(models)

        for model in selected:
            finance_ratio = model.FINEXPE / model.BIZINCO * 100
            management_ratio = model.MANAEXPE / model.BIZINCO * 100
            sales_ratio = model.SALESEXPE / model.BIZINCO * 100
            three_fee_ratio = finance_ratio + management_ratio + sales_ratio

            gross_profit_margin = (model.BIZINCO - model.BIZCOST) / model.BIZINCO * 100
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.ThreeFeeRatio,
                                        Utils.formatFloat(three_fee_ratio, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.FinanceRatio,
                                        Utils.formatFloat(finance_ratio, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.ManagementRatio,
                                        Utils.formatFloat(management_ratio, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.SalesRatio,
                                        Utils.formatFloat(sales_ratio, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.GrossProfitMargin,
                                        Utils.formatFloat(gross_profit_margin, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.NetProfit,
                                        model.NETPROFIT)

        # 资产负债表数据
        models = self.balance_sheet_dao.getByCode(code)
        selected = self._filter_annual_and_latest(models)

        for model in selected:
            account_payable = model.ACCOPAYA + model.COPEPOUN + model.COPEWITHREINRECE + \
                              model.INTEPAYA + model.NOTESPAYA + model.OTHERPAY
            account_receivable = model.ACCORECE + model.DIVIDRECE + model.EXPOTAXREBARECE + model.INTERECE + \
                                 model.NOTESRECE + model.OTHERRECE + model.PREMRECE + model.REINCONTRESE + model.REINRECE
            advance_payment = model.ADVAPAYM
            prepaid = model.PREP
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AccountPayable,
                                        Utils.formatFloat(account_payable / 10000, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AccountReceivable,
                                        Utils.formatFloat(account_receivable / 10000, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AdvancePayment,
                                        Utils.formatFloat(advance_payment / 10000, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.Prepaid,
                                        Utils.formatFloat(prepaid / 10000, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.Upstream,
                                        Utils.formatFloat((account_payable - prepaid) / 10000, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.Downstream,
                                        Utils.formatFloat((advance_payment - account_receivable) / 10000, 2))

        # 现金流量表数据
        models = self.cashflow_dao.getByCode(code)
        selected = self._filter_annual_and_latest(models)
        for model in selected:
            biz_net_cashflow = model.BIZNETCFLOW
            profit_cash_ratio = biz_net_cashflow / profile[model.end_date][ProfileMetric.NetProfit.value]
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.BIZCashFlow,
                                        Utils.formatFloat(biz_net_cashflow / 10000, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.ProfitCashRatio,
                                        Utils.formatFloat(profit_cash_ratio, 2))

        return profile

    def _filter_annual_and_latest(self, models):
        selected = []
        while len(models) > 0 and models[0].end_date.month != 12:
            selected.append(models[0])
            models.pop(0)
        for model in models:
            if model.end_date.month == 12 and model.end_date.year >= 2005:
                selected.append(model)
        return selected

    def display_profile(self, profile):
        columns = list(profile.values())[0].keys()
        for k in profile:
            profile[k] = list(profile[k].values())

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('expand_frame_repr', False)

        # 护城河
        competence_columns = [
            ProfileMetric.GrossProfitMargin,
            ProfileMetric.ROIC,
            ProfileMetric.ThreeFeeRatio,
            ProfileMetric.SalesRatio,
            ProfileMetric.ManagementRatio,
            ProfileMetric.FinanceRatio
        ]
        # 盈利能力
        profit_ability_columns = [
            ProfileMetric.GrossProfitMargin,
            ProfileMetric.NetProfitMargin,
            ProfileMetric.ROE,
            ProfileMetric.ROA,
            ProfileMetric.ProfitCashRatio,
        ]
        # 成长能力
        growth_ability_columns = [
            ProfileMetric.IncomeGrowth,
            ProfileMetric.NetProfitGrowth,
            ProfileMetric.NetProfitCutGrowth,
            ProfileMetric.BIZCashFlow,
            ProfileMetric.FreeCashFlow,
        ]
        # 运营能力
        operation_ability_columns = [
            ProfileMetric.InventoryTurnoverRate,
            ProfileMetric.TotalAssetTurnoverRate,
            ProfileMetric.AccountReceivableTurnoverRate,
        ]
        # 偿债能力
        solvency_ability_columns = [
            ProfileMetric.AssetLiabilityRatio,
            ProfileMetric.CurrentRatio,
            ProfileMetric.QuickRatio,
        ]

        # 杜邦分析
        dupont_analysis_columns = [
            ProfileMetric.ROE,
            ProfileMetric.NetProfitMargin,
            ProfileMetric.TotalAssetTurnoverRate,
            ProfileMetric.EquityMultiplier,  # 注意这个指标数据来自掘金=期末总资产/归属母公司的期末股东权益，采用的不是平均总资产
        ]

        # 上下游分析
        upstream_downstream_columns = [
            ProfileMetric.AccountPayable,
            ProfileMetric.Prepaid,
            ProfileMetric.Upstream,
            ProfileMetric.AccountReceivable,
            ProfileMetric.AdvancePayment,
            ProfileMetric.Downstream,

        ]

        df = pd.DataFrame.from_dict(profile, orient='index', columns=columns)
        print("\n============护城河============")
        print(df[[c.value for c in competence_columns]])

        print("\n============盈利能力============")
        print(df[[c.value for c in profit_ability_columns]])

        print("\n============成长能力============")
        print(df[[c.value for c in growth_ability_columns]])

        print("\n============运营能力============")
        print(df[[c.value for c in operation_ability_columns]])

        print("\n============偿债能力============")
        print(df[[c.value for c in solvency_ability_columns]])

        print("\n============杜邦分析============")
        print(df[[c.value for c in dupont_analysis_columns]])

        print("\n============上下游分析============")
        print(df[[c.value for c in upstream_downstream_columns]])


if __name__ == "__main__":
    stock_profile = StockProfile()
    profile = stock_profile.make_profile('002304')
    stock_profile.display_profile(profile)

# coding: utf-8
import math
from datetime import date

import pandas as pd

from goldminer.common.Utils import Utils
from goldminer.models.ProfileMetric import ProfileMetric
from goldminer.models.StockProfileModel import StockProfileModel
from goldminer.storage.BalanceSheetDao import BalanceSheetDao
from goldminer.storage.CashflowStatementDao import CashflowStatementDao
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao
from goldminer.storage.IncomeStatementDao import IncomeStatementDao


class StockProfileFactory:
    def __init__(self):
        self.derivative_dao = DerivativeFinanceIndicatorDao()
        self.income_dao = IncomeStatementDao()
        self.balance_sheet_dao = BalanceSheetDao()
        self.cashflow_dao = CashflowStatementDao()

        self.code = None
        self._stockBars = None

    def _add_metric_to_profile(self, profile: StockProfileModel, end_date: date, metric: ProfileMetric, value):
        profile.add_metric(end_date, metric, value)

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

    def _interest_bearing_liabilities(self, balance_sheet_model):
        """
        来自理杏仁：https://www.lixinger.com/wiki/lwi/
        有息负债 = 负债合计 - 无息流动负债 - 无息非流动负债

        【无息流动负债】 = 【应付票据和应付账款 + 预收款项 + 合同负债 + 应付职工薪酬 + 应交税费 + 其他应付款 + 应付股利 + 应付利息 + 其他流动负债】，该公式也源于神奇网站，其核心思想是这部分是无息的，而除此之外的是有息的，比如应付票据、短期借款、一年内到期的非流动负债等等。
        【无息非流动负债】 = 【非流动负债合计 - 长期借款 - 应付债券】，该公式源于神奇网站，其核心思想是，非流动负债中，除长期借款和应付债券是有息的外，其他全部是无息的。
        对于房地产企业，用户还需要注意其【长期股权投资】、【少数股东权益】以及【对外担保金额变化】等方面的数据。
        自2018年Q3起，大部分公司开始采用新版的会计准则，合同负债从预收账款里分离出来，应付票据和应付账款合并成一个，所以我们也做了相应调整，具体而言就是在无息流动负债里增加了【应付票据】以及【合同负债】。

        :param balance_sheet_model: 资产负债表
        :return:
        """
        model = balance_sheet_model
        interest_free_current_liabilities = model.NOTESPAYA + model.ACCOPAYA + model.ADVAPAYM + model.COPEWORKERSAL + \
                                            model.TAXESPAYA + model.OTHERPAY + model.DIVIPAYA + model.INTEPAYA + \
                                            model.OTHERCURRELIABI

        interest_free_non_current_liabilities = model.TOTALNONCLIAB - model.LONGBORR - model.BDSPAYA
        return model.TOTLIAB - interest_free_current_liabilities - interest_free_non_current_liabilities

    def _interest_liability_coverage(self, interest_bearing_liabilities, balance_sheet_model):
        # 有息利润小于1万当做是0处理，有息负债覆盖率返回最大值1000%
        if math.fabs(interest_bearing_liabilities) < 10000:
            return 1000

        model = balance_sheet_model
        interest_liability_coverage = (model.CURFDS + model.AVAISELLASSE + model.TRADFINASSET + model.PURCRESAASSET +
                                       model.HOLDINVEDUE) / interest_bearing_liabilities * 100
        interest_liability_coverage = min(interest_liability_coverage, 1000)
        interest_liability_coverage = max(interest_liability_coverage, -1000)

        return interest_liability_coverage

    def _interest_liability_ratio(self, interest_bearing_liabilities, balance_sheet_model):
        # 有息利润小于1万当做是0处理，有息负债率返回0
        if math.fabs(interest_bearing_liabilities) < 10000:
            return 0
        return (interest_bearing_liabilities / balance_sheet_model.TOTASSET) * 100

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
        profile = StockProfileModel(code)

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
                                        int(model.FCFF / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.EquityMultiplier,
                                        Utils.formatFloat(model.EM, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.NetProfitCut,
                                        model.NPCUT)
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.ProfitCashRate,
                                        Utils.formatFloat(model.OPNCFTONPCONMS, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.SalesRevenueRate,
                                        Utils.formatFloat(model.SCASHREVTOOPIRT, 2))


        # 利润表数据
        models = self.income_dao.getByCode(code)
        selected = self._filter_annual_and_latest(models)

        for model in selected:
            finance_ratio = model.FINEXPE / model.BIZINCO * 100
            management_ratio = model.MANAEXPE / model.BIZINCO * 100
            sales_ratio = model.SALESEXPE / model.BIZINCO * 100
            three_fee_ratio = finance_ratio + management_ratio + sales_ratio
            core_profit = model.BIZINCO - model.BIZCOST - model.BIZTAX - model.FINEXPE - model.MANAEXPE - model.SALESEXPE
            core_profit_margin = core_profit / model.BIZINCO * 100
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
                                        round(model.NETPROFIT / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.CoreProfit,
                                        core_profit)
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.CoreProfitMargin,
                                        Utils.formatFloat(core_profit_margin, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.CoreProfitRate,
                                        Utils.formatFloat(core_profit / model.PERPROFIT, 2))

        # 资产负债表数据
        models = self.balance_sheet_dao.getByCode(code)
        selected = self._filter_annual_and_latest(models)

        for model in selected:
            account_payable = model.ACCOPAYA + model.COPEPOUN + model.COPEWITHREINRECE + \
                              model.INTEPAYA + model.NOTESPAYA + model.OTHERPAY
            account_receivable = model.ACCORECE + model.DIVIDRECE + model.EXPOTAXREBARECE + model.INTERECE + \
                                 model.NOTESRECE + model.OTHERRECE + model.PREMRECE + model.REINCONTRESE + \
                                 model.REINRECE
            advance_payment = model.ADVAPAYM
            prepaid = model.PREP
            occupation = account_payable - prepaid + advance_payment - account_receivable
            goodwill_rate = model.GOODWILL / model.RIGHAGGR
            interest_bearing_liabilities = self._interest_bearing_liabilities(model)
            interest_liability_ratio = self._interest_liability_ratio(interest_bearing_liabilities, model)
            interest_liability_coverage = self._interest_liability_coverage(interest_bearing_liabilities, model)

            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AccountPayable,
                                        round(account_payable / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AccountReceivable,
                                        round(account_receivable / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.AdvancePayment,
                                        round(advance_payment / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.Prepaid,
                                        round(prepaid / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.Upstream,
                                        round((account_payable - prepaid) / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.Downstream,
                                        round((advance_payment - account_receivable) / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.Occupation,
                                        round(occupation / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.GoodwillRate,
                                        round(goodwill_rate / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.InterestLiabilityRatio,
                                        Utils.formatFloat(interest_liability_ratio, 2))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.InterestLiabilityCoverage,
                                        int(interest_liability_coverage))

        # 现金流量表数据
        models = self.cashflow_dao.getByCode(code)
        selected = self._filter_annual_and_latest(models)
        for model in selected:
            biz_net_cashflow = model.BIZNETCFLOW
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.BIZCashFlow,
                                        round(biz_net_cashflow / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.InvestCashFlow,
                                        round(model.INVNETCASHFLOW / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.FinancialCashFlow,
                                        round(model.FINNETCFLOW / 1000000))
            self._add_metric_to_profile(profile, model.end_date, ProfileMetric.CapitalExp,
                                        round(model.ACQUASSETCASH / 1000000))

        return profile

    def _filter_annual_and_latest(self, models):
        selected = []
        while len(models) > 0 and models[0].end_date.month != 12:
            selected.append(models[0])
            models.pop(0)
        count = 0
        for model in models:
            if model.end_date.month == 12 and model.end_date.year >= 2005:
                selected.append(model)
                count += 1
            if count >= 10:
                break
        return selected

    def _filter_annual_df(self, df: pd.DataFrame):
        indexes = df.index.values.tolist()
        filtered_indexes = []
        for d in indexes:
            if d.month == 12:
                filtered_indexes.append(d)
        return df.loc[pd.Index(filtered_indexes)]

    def _sum_df(self, df: pd.DataFrame):
        df = self._filter_annual_df(df)
        df.loc["SUM"] = df.sum()
        return df

    def _mean_df(self, df: pd.DataFrame, precision=None):
        df = self._filter_annual_df(df)
        if precision:
            df.loc["MEAN"] = df.mean().apply(lambda x: Utils.formatFloat(x, 2))
        else:
            df.loc["MEAN"] = df.mean()
        return df

    def display_profile(self, profile):
        profile = profile.as_dict()
        columns = list(profile.values())[0].keys()
        for k in profile:
            profile[k] = list(profile[k].values())

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('expand_frame_repr', False)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('colheader_justify', 'left')
        pd.set_option('display.width', 200)

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
            ProfileMetric.CoreProfitMargin,
            ProfileMetric.NetProfitMargin,
            ProfileMetric.ROE,
            ProfileMetric.ROA,
            ProfileMetric.ProfitCashRate,
            ProfileMetric.CoreProfitRate,
        ]
        # 成长能力
        growth_ability_columns = [
            ProfileMetric.IncomeGrowth,
            ProfileMetric.NetProfitGrowth,
            ProfileMetric.NetProfitCutGrowth,
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
            ProfileMetric.InterestLiabilityRatio,
            ProfileMetric.InterestLiabilityCoverage,
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
            ProfileMetric.Occupation,
        ]

        # 现金流
        cash_flow_columns = [
            ProfileMetric.NetProfit,
            ProfileMetric.BIZCashFlow,
            ProfileMetric.InvestCashFlow,
            ProfileMetric.FinancialCashFlow,
            ProfileMetric.FreeCashFlow,
            ProfileMetric.CapitalExp,
        ]

        # 排雷指标
        risk_signal_columns = [
            ProfileMetric.InventoryTurnoverRate,
            ProfileMetric.AccountReceivableTurnoverRate,
            ProfileMetric.SalesRevenueRate,
            ProfileMetric.GoodwillRate,
            ProfileMetric.AssetLiabilityRatio,
        ]

        df = pd.DataFrame.from_dict(profile, orient='index', columns=columns)
        df.columns = df.columns.map(lambda x: x.value)
        print("\n============护城河============")
        competence_df = df[[c.value for c in competence_columns]].copy()
        competence_df.loc["MEAN"] = competence_df.mean().apply(lambda x: Utils.formatFloat(x, 2))
        print(competence_df)

        print("\n============盈利能力============")
        profit_ability_df = df[[c.value for c in profit_ability_columns]].copy()
        profit_ability_df.loc["MEAN"] = profit_ability_df.mean().apply(lambda x: Utils.formatFloat(x, 2))
        print(profit_ability_df)

        print("\n============成长能力============")
        growth_ability_df = df[[c.value for c in growth_ability_columns]].copy()
        growth_ability_df.loc["MEAN"] = growth_ability_df.mean().apply(lambda x: Utils.formatFloat(x, 2))
        print(growth_ability_df)

        print("\n============运营能力============")
        operation_ability_df = df[[c.value for c in operation_ability_columns]].copy()
        operation_ability_df.loc["MEAN"] = operation_ability_df.mean().apply(lambda x: Utils.formatFloat(x, 2))
        print(operation_ability_df)

        print("\n============偿债能力============")
        solvency_ability_df = df[[c.value for c in solvency_ability_columns]].copy()
        solvency_ability_df = self._mean_df(solvency_ability_df, 2)
        print(solvency_ability_df)

        print("\n============杜邦分析============")
        dupond_df = df[[c.value for c in dupont_analysis_columns]]
        dupond_df = self._mean_df(dupond_df, 2)
        print(dupond_df)

        print("\n============上下游分析============")
        print(df[[c.value for c in upstream_downstream_columns]])

        print("\n============现金流============")
        cash_flow_df = df[[c.value for c in cash_flow_columns]]
        cash_flow_df = self._sum_df(cash_flow_df)
        print(cash_flow_df)

        print("\n============排雷指标============")
        risk_df = df[[c.value for c in risk_signal_columns]]
        risk_df = self._mean_df(risk_df, 2)
        print(risk_df)


if __name__ == "__main__":
    stock_profile = StockProfileFactory()
    profile = stock_profile.make_profile('603600')
    stock_profile.display_profile(profile)

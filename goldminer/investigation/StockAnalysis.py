# coding: utf-8
from typing import List

import pandas as pd

from goldminer.investigation.StockProfileFactory import StockProfileFactory
from goldminer.models.ProfileMetric import ProfileMetric
from goldminer.models.StockProfileModel import StockProfileModel
from goldminer.storage.StockDao import StockDao


class StockAnalysis:
    def __init__(self):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('expand_frame_repr', False)

        self.__stock_dao = StockDao()
        self.__stocks = {}

        self.__report = {}
        # 护城河
        self.__competence_columns = [
            ProfileMetric.ROE,
            ProfileMetric.GrossProfitMargin,
            ProfileMetric.ThreeFeeRatio,
            # ProfileMetric.SalesRatio,
            # ProfileMetric.ManagementRatio,
            # ProfileMetric.FinanceRatio
        ]
        # 盈利能力
        self.__profit_ability_columns = [
            ProfileMetric.GrossProfitMargin,
            ProfileMetric.NetProfitMargin,
            ProfileMetric.ROE,
            ProfileMetric.ROA,
            ProfileMetric.ProfitCashRatio,
        ]
        # 成长能力
        self.__growth_ability_columns = [
            ProfileMetric.IncomeGrowth,
            ProfileMetric.NetProfitGrowth,
            ProfileMetric.NetProfitCutGrowth,
            ProfileMetric.BIZCashFlow,
            ProfileMetric.FreeCashFlow,
        ]
        # 运营能力
        self.__operation_ability_columns = [
            ProfileMetric.InventoryTurnoverRate,
            ProfileMetric.TotalAssetTurnoverRate,
            ProfileMetric.AccountReceivableTurnoverRate,
        ]
        # 偿债能力
        self.__solvency_ability_columns = [
            ProfileMetric.AssetLiabilityRatio,
            ProfileMetric.CurrentRatio,
            ProfileMetric.QuickRatio,
        ]

        # 杜邦分析
        self.__dupont_analysis_columns = [
            ProfileMetric.ROE,
            ProfileMetric.NetProfitMargin,
            ProfileMetric.TotalAssetTurnoverRate,
            ProfileMetric.EquityMultiplier,  # 注意这个指标数据来自掘金=期末总资产/归属母公司的期末股东权益，采用的不是平均总资产
        ]

        # 上下游分析
        self.__upstream_downstream_columns = [
            ProfileMetric.AccountPayable,
            ProfileMetric.Prepaid,
            ProfileMetric.Upstream,
            ProfileMetric.AccountReceivable,
            ProfileMetric.AdvancePayment,
            ProfileMetric.Downstream,
            ProfileMetric.Occupation,
        ]

    def __average_n(self, data, n):
        i = 0
        sum = 0
        for end_date in data:
            if i >= n:
                break
            if end_date.month == 12:
                sum += data[end_date]
                i += 1
        return sum / i

    def __get_stock(self, code):
        if code not in self.__stocks:
            model = self.__stock_dao.getByCode(code)
            if model:
                self.__stocks[code] = model
        if code in self.__stocks:
            return self.__stocks[code]
        else:
            return None

    def transform_profiles_to_report(self, profiles: List[StockProfileModel]):
        report = {}
        for profile in profiles:
            code = profile.get_code()
            stock_model = self.__get_stock(code)
            profile_dict = profile.as_dict()
            for end_date in profile_dict:
                for metric in profile_dict[end_date]:
                    if metric not in report:
                        report[metric] = {}
                    if stock_model not in report[metric]:
                        report[metric][stock_model] = {}
                    report[metric][stock_model][end_date] = profile_dict[end_date][metric]

        # Calculate 10 year average, 5 year average
        for metric in report:
            for stock_model in report[metric]:
                ave5 = self.__average_n(report[metric][stock_model], 5)
                ave10 = self.__average_n(report[metric][stock_model], 10)
                report[metric][stock_model]['ave5'] = ave5
                report[metric][stock_model]['ave10'] = ave10

        return report
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.max_rows', None)
        # pd.set_option('expand_frame_repr', False)
        #
        # df = pd.DataFrame.from_dict(report[ProfileMetric.ROIC], orient='index')
        # print(df)
        # return df

    def display_report(self, report):
        print("\n============护城河============")
        for metric in self.__competence_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='ave10', axis=0, ascending=False)
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============盈利能力============")
        for metric in self.__profit_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='ave10', axis=0, ascending=False)
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============成长能力============")
        for metric in self.__growth_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='ave10', axis=0, ascending=False)
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============运营能力============")
        for metric in self.__operation_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='ave10', axis=0, ascending=False)
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============偿债能力============")
        for metric in self.__solvency_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='ave10', axis=0, ascending=False)
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============杜邦分析============")
        for metric in self.__dupont_analysis_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='ave10', axis=0, ascending=False)
            print("\n---------" + metric.value + "---------")
            print(df)


if __name__ == "__main__":
    analysis = StockAnalysis()
    profile_factory = StockProfileFactory()
    profiles = []
    codes = ['603288', '603027']
    for code in codes:
        profiles.append(profile_factory.make_profile(code))

    report = analysis.transform_profiles_to_report(profiles)
    analysis.display_report(report)

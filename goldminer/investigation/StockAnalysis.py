# coding: utf-8
import datetime
import math
from typing import List

import pandas as pd

from goldminer.common.Utils import Utils
from goldminer.investigation.StockProfileFactory import StockProfileFactory
from goldminer.models.ProfileMetric import ProfileMetric
from goldminer.models.StockProfileModel import StockProfileModel
from goldminer.storage.StockDao import StockDao


class StockAnalysis:
    def __init__(self):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('expand_frame_repr', False)
        pd.set_option('colheader_justify', 'left')

        self.__stock_dao = StockDao()
        self.__stocks = {}

        self.__report = {}
        # 护城河
        self.__competence_columns = [
            ProfileMetric.ROE,
            ProfileMetric.GrossProfitMargin,
            ProfileMetric.ThreeFeeRatio,
        ]
        # 盈利能力
        self.__profit_ability_columns = [
            ProfileMetric.GrossProfitMargin,
            ProfileMetric.CoreProfitMargin,
            ProfileMetric.NetProfitMargin,
            ProfileMetric.ROE,
            ProfileMetric.ROA,
            ProfileMetric.ProfitCashRate,
            ProfileMetric.CoreProfitRate,
        ]
        # 成长能力
        self.__growth_ability_columns = [
            ProfileMetric.IncomeGrowth,
            ProfileMetric.NetProfitGrowth,
            ProfileMetric.NetProfitCutGrowth,
        ]
        # 运营能力
        self.__operation_ability_columns = [
            ProfileMetric.InventoryTurnoverRate,
            ProfileMetric.TotalAssetTurnoverRate,
            ProfileMetric.AccountReceivableTurnoverRate,
            ProfileMetric.SalesRevenueRate,
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

        # 现金流量表
        self.__cash_flow_columns = [
            ProfileMetric.BIZCashFlow,
            ProfileMetric.InvestCashFlow,
            ProfileMetric.FinancialCashFlow,
            ProfileMetric.FreeCashFlow,
            ProfileMetric.CapitalExp
        ]

        # 资产负债表质量
        self.__balance_sheet_quality_columns = [
            ProfileMetric.AssetLiabilityRatio,
            ProfileMetric.GoodwillRate,
            ProfileMetric.OtherReceivableRatio,
            ProfileMetric.OtherPayRatio,
            ProfileMetric.AccountReceivableRatio,
        ]

        # 资产负债表结构
        self.__balance_sheet_structure_columns = [
            ProfileMetric.MonetaryFundsRatio,
            ProfileMetric.OperatingAssetRatio,
            ProfileMetric.ProductAssetRatio,
            ProfileMetric.InvestmentAssetRatio,
        ]

    def _mean(self, data, n):
        i = 0
        sum = 0
        for end_date in data:
            if not isinstance(end_date, datetime.date):
                continue
            if i >= n:
                break
            if end_date.month == 12:
                sum += data[end_date]
                i += 1
        return Utils.formatFloat(sum / i, 2)

    # 计算增长率的复合增速
    def _compound_mean(self, data, n):
        growths = []
        i = 0
        total = 1
        for end_date in data:
            if not isinstance(end_date, datetime.date):
                continue
            if i >= n:
                break
            if end_date.month == 12:
                growths.append(data[end_date])
                i += 1
        if len(growths) == 0:
            return 0

        growths.reverse()
        for g in growths:
            total = math.fabs(total) * (1 + g / 100)

        compound_growth = Utils.formatFloat(math.pow(math.fabs(total), 1 / len(growths)) * 100 - 100, 2)
        return compound_growth if total > 0 else -compound_growth

    def _sum(self, data, n):
        i = 0
        sum = 0
        for end_date in data:
            if not isinstance(end_date, datetime.date):
                continue
            if i >= n:
                break
            if end_date.month == 12:
                sum += data[end_date]
                i += 1
        return int(sum)

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
                if metric in [ProfileMetric.IncomeGrowth, ProfileMetric.NetProfitCutGrowth,
                              ProfileMetric.NetProfitGrowth]:
                    report[metric][stock_model]['MEAN5'] = self._compound_mean(report[metric][stock_model], 5)
                    report[metric][stock_model]['MEAN10'] = self._compound_mean(report[metric][stock_model], 10)
                elif metric in [ProfileMetric.BIZCashFlow, ProfileMetric.InvestCashFlow,
                                ProfileMetric.FinancialCashFlow,
                                ProfileMetric.FreeCashFlow, ProfileMetric.CapitalExp]:
                    report[metric][stock_model]['SUM5'] = self._sum(report[metric][stock_model], 5)
                    report[metric][stock_model]['SUM10'] = self._sum(report[metric][stock_model], 10)
                else:
                    report[metric][stock_model]['MEAN5'] = self._mean(report[metric][stock_model], 5)
                    report[metric][stock_model]['MEAN10'] = self._mean(report[metric][stock_model], 10)

        return report

    def move_column_to_head(self, df, column):
        column_data = df[column]
        df = df.drop(column, axis=1)
        df.insert(0, column, column_data)
        return df

    def display_report(self, report):
        print("\n============护城河============")
        for metric in self.__competence_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============盈利能力============")
        for metric in self.__profit_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============成长能力============")
        for metric in self.__growth_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============运营能力============")
        for metric in self.__operation_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============偿债能力============")
        for metric in self.__solvency_ability_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============杜邦分析============")
        for metric in self.__dupont_analysis_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============现金流============")
        for metric in self.__cash_flow_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='SUM5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "SUM10")
            df = self.move_column_to_head(df, "SUM5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============资产负债表质量============")
        for metric in self.__balance_sheet_quality_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)

        print("\n============资产负债表质量============")
        for metric in self.__balance_sheet_structure_columns:
            df = pd.DataFrame.from_dict(report[metric], orient='index')
            df = df.rename(lambda x: x.name, axis=0)
            df = df.sort_values(by='MEAN5', axis=0, ascending=False)
            df = self.move_column_to_head(df, "MEAN10")
            df = self.move_column_to_head(df, "MEAN5")
            print("\n---------" + metric.value + "---------")
            print(df)


if __name__ == "__main__":
    analysis = StockAnalysis()
    profile_factory = StockProfileFactory()
    profiles = []

    codes = ['600580', '002249', '002176', '300660', '603728', '000922', '603583', '002801']
    for code in codes:
        profiles.append(profile_factory.make_profile(code))

    report = analysis.transform_profiles_to_report(profiles)
    analysis.display_report(report)

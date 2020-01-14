# coding: utf-8
import os

import pdfplumber
from pdfplumber import PDF

from goldminer.common import GMConsts
from goldminer.common.FinancialReportType import FinancialReportType


class ReportExtractor:
    def load_report(self, code, year, report_type: FinancialReportType):
        file = GMConsts.FINANCIAL_REPORT_ROOT + "{}/{}/{}.pdf".format(code, year, report_type.value)
        if not os.path.exists(file):
            raise Exception("Could not find report {}".format(file))
        return pdfplumber.open(file)

    def is_table_major_biz(self, table):
        keywords = ["分行业", "分产品", "分地区"]
        str = ""
        for row in table:
            for col in row:
                if col is not None:
                    str += col
        # print(str)
        count = 0
        for k in keywords:
            if k in str:
                count += 1
        if count > 1:
            print(table)
            return True

    def extract_major_biz_info(self, report: PDF):
        for page in report.pages:
            tables = page.extract_tables()
            for table in tables:
                # print(table)
                if self.is_table_major_biz(table):
                    return table


if __name__ == "__main__":
    extractor = ReportExtractor()
    report = extractor.load_report('300357', 2018, FinancialReportType.Annual)
    extractor.extract_major_biz_info(report)

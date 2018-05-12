# -*- coding: utf-8 -*-

import io
import sys
import unittest

from lib.HTMLTestRunner import HTMLTestRunner
# ------------------------------------------------------------------------
# This is the main test on HTMLTestRunner
from tests.IndexConstituentDaoTest import IndexConstituentDaoTest
from tests.IndexDailyBarDaoTest import IndexDailyBarDaoTest
from tests.IndexesDaoTest import IndexesDaoTest
from tests.StockDailyBarAdjustNoneDaoTest import StockDailyBarAdjustNoneDaoTest
from tests.StockDaoTest import StockDaoTest
from tests.StockFundamentalsDaoTest import StockFundamentalsDaoTest


class HTMLTestSuite(unittest.TestCase):

    def test0(self):
        self.suite = unittest.TestSuite()
        buf = io.StringIO()
        runner = HTMLTestRunner(buf)
        runner.run(self.suite)
        # didn't blow up? ok.
        self.assertTrue('</html>' in buf.getvalue())

    def test_main(self):
        # Run HTMLTestRunner. Verify the HTML report.

        # suite of TestCases
        self.suite = unittest.TestSuite()
        self.suite.addTests([
            unittest.defaultTestLoader.loadTestsFromTestCase(StockDaoTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(IndexesDaoTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(StockDailyBarAdjustNoneDaoTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(IndexDailyBarDaoTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(IndexConstituentDaoTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(StockFundamentalsDaoTest)
            ])

        # Invoke TestRunner
        file_path = "result.html"
        file_result = open(file_path, 'w')
        runner = HTMLTestRunner(
                    stream=file_result,
                    title='Gold Miner Tests',
                    description='This demonstrates the report output by HTMLTestRunner.'
                    )
        runner.run(self.suite)
        file_result.close()


##############################################################################
# Executing this module from the command line
##############################################################################

import unittest
if __name__ == "__main__":
    if len(sys.argv) > 1:
        argv = sys.argv
    else:
        argv=['HTMLTestSuite.py', 'HTMLTestSuite']
    unittest.main(argv=argv)

    # Testing HTMLTestRunner with HTMLTestRunner would work. But instead
    # we will use standard library's TextTestRunner to reduce the nesting
    # that may confuse people.
    #HTMLTestRunner.main(argv=argv)


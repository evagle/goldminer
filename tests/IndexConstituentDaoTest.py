import unittest
from datetime import date

from storage.IndexConstituentDao import IndexConstituentDao


class IndexConstituentDaoTest(unittest.TestCase):

    def setUp(self):
        self.dao = IndexConstituentDao()

    def testGetLatestDate(self):
        d = self.dao.getLatestDate('000001')
        self.assertLess(date(2018, 3, 1), d)

        d = self.dao.getLatestDate('none')
        self.assertEqual(date(2001, 1, 1), d)


if __name__ == '__main__':
    unittest.main()






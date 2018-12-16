import unittest
from datetime import date

from goldminer.models.models import Indexes
from goldminer.storage.IndexesDao import IndexesDao


class IndexesDaoTest(unittest.TestCase):

    def setUp(self):
        self.dao = IndexesDao()

    def testGetAll(self):
        result = self.dao.all()
        self.assertTrue(len(result) > 10)
        self.assertEqual(type(result[0]), Indexes)

    def testGetIndexList(self):
        result = self.dao.getIndexList()
        self.assertTrue(len(result) > 10)

    def testGetIndexPublishDate(self):
        d = self.dao.getIndexPublishDate('000001')
        self.assertEqual(date(1991, 7, 15), d)

        d = self.dao.getIndexPublishDate('none')
        self.assertEqual(None, d)


if __name__ == '__main__':
    unittest.main()






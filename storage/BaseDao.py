# coding: utf-8

from storage.DBHelper import DBHelper


class BaseDao:
    def __init__(self):
        self.session = DBHelper.getSession()
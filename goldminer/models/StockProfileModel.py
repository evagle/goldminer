# coding: utf-8
from datetime import date

from goldminer.models.ProfileMetric import ProfileMetric


class StockProfileModel:
    def __init__(self, code):
        self.__code = code
        self.__profile = {}

    def add_metric(self, end_date: date, metric: ProfileMetric, value):
        if end_date not in self.__profile:
            self.__profile[end_date] = {}
        self.__profile[end_date][metric] = value
        return self

    def get_code(self):
        return self.__code

    def get_metric(self, end_date, metric: ProfileMetric):
        if end_date in self.__profile and metric in self.__profile[end_date]:
            return self.__profile[end_date][metric]
        return None

    def as_dict(self):
        return self.__profile

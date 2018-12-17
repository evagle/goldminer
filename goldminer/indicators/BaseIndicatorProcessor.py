# coding: utf-8
from abc import abstractmethod


class BaseIndicatorProcessor:
    @abstractmethod
    def process(self, code, **kwargs):
        '''
        please implement this function
        :param indexCode:
        :return:
        '''

    def get_args(self, kwargs: dict, key: str, default=None):
        return kwargs[key] if key in kwargs else default

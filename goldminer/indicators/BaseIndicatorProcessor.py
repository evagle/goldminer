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

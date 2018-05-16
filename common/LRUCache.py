# coding: utf-8

import collections


class LRUCache:

    def __init__(self, size=5):
        self.size = size,
        self.cache = collections.OrderedDict()

    def get(self, key):
        if key in self.cache.keys():
            val = self.cache.pop(key)
            self.cache[key] = val
        else:
            val = None

        return val

    def set(self, key, val):
        if key in self.cache.keys():
            val = self.cache.pop(key)
            self.cache[key] = val
        else:
            if len(self.cache) == self.size:
                self.cache.popitem(last=False)
                self.cache[key] = val
            else:
                self.cache[key] = val

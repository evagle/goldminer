# coding: utf-8
from common.Utils import Utils
from storage.DBHelper import DBHelper


class BaseDao:
    def __init__(self):
        self.session = DBHelper.getSession()

    def _addAll(self, modelClazz, instances):
        properties = Utils.getPropertiesOfClazz(modelClazz)
        items = []
        for instance in instances:
            item = {}
            for p in properties:
                item[p] = getattr(instance, p)
            items.append(item)

        self.session.execute(
            modelClazz.__table__.insert(),
            items
        )
        self.session.commit()

    def getSession(self):
        return self.session

# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://pocketpet:3MjdvUuXqxca6cbc@unionfight.citypet.cn:3306/goldminer?charset=utf8', pool_recycle=60)


class DBHelper:
    __DBSessionClass = sessionmaker(bind=engine)
    __session = __DBSessionClass()

    @staticmethod
    def getSession() -> Session:
        return DBHelper.__session

    @staticmethod
    def getEngine():
        return engine


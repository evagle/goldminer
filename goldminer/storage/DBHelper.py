# coding: utf-8
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker



class DBHelper:
    __engine = create_engine('mysql+pymysql://pocketpet:3MjdvUuXqxca6cbc@localhost:3307/goldminer?charset=utf8',
                           pool_recycle=60)
    __DBSessionClass = sessionmaker(bind=__engine)
    __session = __DBSessionClass()
    __pymysql_conn = pymysql.connect(host="localhost", port=3307, user='pocketpet', password='3MjdvUuXqxca6cbc', db='goldminer')

    @staticmethod
    def getSession() -> Session:
        return DBHelper.__session

    @staticmethod
    def getEngine():
        return DBHelper.__engine

    @staticmethod
    def getPymysqlConn():
        return DBHelper.__pymysql_conn

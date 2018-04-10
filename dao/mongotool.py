# -*- coding:utf-8-*-
import logging

from pymongo import MongoClient

from config.config import config
from utils.myexception import MongoDBTypeNotMatchException, MongoAssistInitialException

_uri = 'mongodb://%s:27017/' % config['db_host']
_db_name = config['db_name']
_client = MongoClient(_uri)
_db = _client.get_database(_db_name)
_tables = {}


class AssistColumnClass:
    """
    该类用于在申明table时作为辅助列
    """
    def __init__(self, type_=None):
        if type_ is not None:
            if type(type_) is not type:
                raise MongoAssistInitialException('type_ must be a `type`, such as `int`')
        self.type_ = type_


class TableMeta(type):
    """
    Table的metaclass，自动将其子类中定义的AssistColumnClass删除，
    同时将将__table__替换成对应的db.table对象连接
    如果此前已有连接，则采用此前的连接
    如果此前不存在连接，则新建一个连接
    """

    def __new__(mcs, name, bases, attrs):
        if name == 'Table':
            return type.__new__(mcs, name, bases, attrs)

        # connect table to attrs['table']
        table_name = attrs.get('__table__', None) or name
        if table_name not in _tables:
            _tables[table_name] = _db[table_name]
        attrs['__table__'] = _tables[table_name]
        attrs['__table_name__'] = table_name
        attrs['__type_map__'] = {}

        # delete all assist attr
        tmp = []
        for k, v in attrs.items():
            if isinstance(v, AssistColumnClass):
                tmp.append(k)

        for k in tmp:
            if attrs[k].type_ is not None:
                # 如果辅助类中定义了类型的话，就把类型记下来，
                # 方便之后做限制
                attrs['__type_map__'][k] = attrs[k].type_
            attrs.pop(k)

        return type.__new__(mcs, name, bases, attrs)


class Table(metaclass=TableMeta):
    """
    有新的Collection（table）时，继承该类，
    需要定义__table__为表名
    如有需要可以用AssistColumnClass来定义一些辅助列

    所有的数据存储在__data__中
    __table__会被替换成db.table
    """

    def __init__(self):
        self.__data__ = {}

    def __getattr__(self, key):
        # if key.startswith('__'):
        #     return self.__dict__.get(key)
        # 上面两步其实没有必要，因为默认会先调用自建的__getattribute__
        # 从__dict__中取值，然后从类变量中取值
        # 如果都找不到最后才会走这个方法
        return self.__data__.get(key)

    def __setattr__(self, key, value):
        if key.startswith('__'):
            self.__dict__[key] = value
        else:
            if key in self.__type_map__ and type(value) is not self.__type_map__[key]:
                # 如果写了类型限制，但当前赋值类型与限制类型不同，抛出Exception
                raise MongoDBTypeNotMatchException(
                    'type not match in table `%s`, at key `%s`,'
                    'require type: `%s`,'
                    'get type: `%s`' % (
                        self.__table_name__,
                        key,
                        str(self.__type_map__[key]),
                        type(value)
                    )
                )
            self.__data__[key] = value

    def load(self, key_date=None):
        """

        :param key_date: 为None时，直接采用当前对象中的数据load对象，非None时，清空当前数据，
        并采用key_date载入新的数据对象
        :return:是否插入成功
        """
        if key_date is None:
            items = self.__table__.find_one(self.__data__)
        else:
            self.__data__.clear()
            items = self.__table__.find_one(key_date)

        if items is None:
            logging.warning('can not load data')
            return False
        else:
            self.__data__ = items
            return True

    def commit(self):
        if self.__data__ is None:
            logging.warning('can not commit to mongodb since date is None')
            return False

        if self._id is not None:
            self.__table__.replace_one({'_id': self._id}, self.__data__)
        else:
            _id = self.__table__.insert_one(self.__data__).inserted_id
            self.__data__['_id'] = _id
        return True

    def delete(self):
        if len(self.__data__) == 0:
            logging.warning('need defined data before delete')
            return
        self.__table__.delete_one(self.__data__)
        self.__data__.clear()

    def delete_all(self):
        self.__table__.delete_many({})
        self.__data__.clear()

    def find_all(self, start=None, end=None, row=None):
        """

        :param row: 行数，如果没有定义end的时候有效
        :param start: 从第几行开始 0为第一行，即不跳过任何一行
        :param end: 结束到第几行，总的返回行数为end-start
        :return: 如果都是None的话，就返回所有的内容（返回类型为generator）
        """
        data = self.__table__.find(self.__data__)
        if start is not None:
            data = data.skip(start)
        else:
            start = 0

        if end is not None:
            if end > start:
                data = data.limit(end - start)
        elif row is not None:
            data = data.limit(row)

        return (x for x in data)


import unittest

from dao.mongotool import Table, AssistColumnClass
from dao.my_mongodb_exception import MongoDBTypeNotMatchException, MongoAssistInitialException


class TestMongoTool(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_error_column(self):
        """
        测试在column定义不是AssistColumnClass时候是否正确抛出异常
        :return:
        """
        with self.assertRaises(MongoAssistInitialException):
            class ErrorColumn(Table):
                __table__ = 'test'
                id = AssistColumnClass('123')

            u = ErrorColumn()
            u.id = 123

    def test_error_type(self):
        """
        测试column加入限制以后，是否能正确检测出错误
        :return:
        """
        with self.assertRaises(MongoDBTypeNotMatchException):
            class ErrorType(Table):
                __table__ = 'test'
                id = AssistColumnClass(int)

            u = ErrorType()
            u.id = '123'

    def test_normal(self):
        """
        测试常规通过情况
        :return:
        """

        class TestClass(Table):
            __table__ = 'test'
            id = AssistColumnClass(int)
            str_value = AssistColumnClass(str)
            normal_value = AssistColumnClass(is_not_none=True)

        u = TestClass()
        u.id = 1
        u.str_value = '1'
        self.assertEqual(u.commit(), False)
        u.normal_value = 1
        u.commit()
        u.delete_all()
        u.id = 1
        u.str_value = '1'
        u.normal_value = 1
        u.commit()
        u.normal_value = '1'
        u.commit()
        u = TestClass()
        u.id = 1
        u.load()
        self.assertEqual(u.normal_value, '1')
        self.assertEqual(u.str_value, '1')
        u.delete()
        u.id = 1
        self.assertEqual(u.load(), False)
        self.assertEqual(u.str_value, None)


if __name__ == '__main__':
    unittest.main()

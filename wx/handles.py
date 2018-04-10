# -*-coding:utf-8-*-
import functools
import sys

from wx.tools import build_wx_response_xml_b

from dao.myredis import redis_client
from dao.models import *
from config.config import config

admin_pswd = config['wx_admin_pswd']
instruct_awake_func = {}
instruct_handles_func = {}


def awake(instruct):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__awake__ = instruct
        return wrapper

    return decorator


def handle(instruct):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__handle__ = instruct
        return wrapper

    return decorator


@handle('1')
def cdkey_handle(user_id, self_id, user_input, user_input_before):
    if user_input_before.get('game_account') is not None:
        # TODO 使用注册码
        is_cdkey_legal, day_remain = '', ''
        if is_cdkey_legal:
            resp = 'CDKey使用成功，当前剩余可用天数%s' % day_remain
        else:
            resp = '无效CDKEY'
        redis_client.delete(user_id)
        return build_wx_response_xml_b(
            user_id,
            self_id,
            resp
        )
    else:
        redis_client.hset(user_id, 'game_account', user_input)
        return build_wx_response_xml_b(
            user_id,
            self_id,
            "请输入CDKEY"
        )


@awake('1')
def cdkey_awake(user_id, self_id):
    return build_wx_response_xml_b(
        user_id,
        self_id,
        '请输入您的hustle castle游戏账号'
    )


@awake('10000')
def add_day_awake(user_id, self_id):
    return build_wx_response_xml_b(
        user_id,
        self_id,
        '请输入管理员密码'
    )


@handle('10000')
def add_day_handle(user_id, self_id, user_input, user_input_before):
    if 'admin_pswd' not in user_input_before:
        if user_input == admin_pswd:
            redis_client.hset(user_id, 'admin_pswd', user_input)
            return build_wx_response_xml_b(
                user_id,
                self_id,
                '请输入要充值的game_id与天数:如 100000-10表示给100000加上10天'
            )
    pass


@awake('10001')
def add_get_users_awake(user_id, self_id):
    return build_wx_response_xml_b(
        user_id,
        self_id,
        "请输入管理员密码"
    )


@handle('10001')
def add_get_users_handle(user_id, self_id, user_input, user_input_before):
    if 'admin_pswd' not in user_input_before:
        if user_input == admin_pswd:
            redis_client.hset(user_id, 'admin_pswd', user_input)
            return build_wx_response_xml_b(
                user_id,
                self_id,
                '请输入要查询的起始位置与结束位置:如 1-100 表示查询1到100位'
            )
    # TODO 返回所有找找到的信息


@awake('10002')
def add_get_user_awake(user_id, self_id):
    return build_wx_response_xml_b(
        user_id,
        self_id,
        "请输入管理员密码"
    )


@handle('10002')
def add_get_user_handle(user_id, self_id, user_input, user_input_before):
    if 'admin_pswd' not in user_input_before:
        if user_input == admin_pswd:
            redis_client.hset(user_id, 'admin_pswd', user_input)
            return build_wx_response_xml_b(
                user_id,
                self_id,
                '请输入要查询的game_id'
            )
    # TODO 返回所有找找到的信息


def init_model():
    mod = sys.modules[__name__]
    for attr in dir(mod):
        fn = getattr(mod, attr)
        if callable(fn):
            instruct_awake = getattr(fn, '__awake__', None)
            instruct_handle = getattr(fn, '__handle__', None)
            if instruct_awake:
                instruct_awake_func[instruct_awake] = fn
            if instruct_handle:
                instruct_handles_func[instruct_handle] = fn


def add_handle(module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n + 1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        fn = getattr(mod, attr)
        if callable(fn):
            instruct_awake = getattr(fn, '__awake__', None)
            instruct_handle = getattr(fn, '__handle__', None)
            if instruct_awake:
                instruct_awake_func[instruct_awake] = fn
            if instruct_handle:
                instruct_handles_func[instruct_handle] = fn


init_model()

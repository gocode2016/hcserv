# -*- coding:utf-8 -*-
import datetime

import requests

from utils.tools import md5
from config.config import config

local = True

local = not local

if local:
    port = '5000'
    host = 'localhost'
else:
    port = '80'
    host = config['server_host']


def verify(game_id):
    """
    模拟客户端请求veirfy接口
    :param game_id:
    """
    request_time = int(datetime.datetime.now().timestamp())
    request_secret = md5('%s%s' % (game_id[:5], request_time))
    data = {
        'game_id': game_id,
        'secret': request_secret,
        'time': request_time
    }
    r = requests.get(
        'http://%s:%s/hcserv/verify' % (host, port),
        params=data
    ).text
    print(r)


verify('1724401')

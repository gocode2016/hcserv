# -*-coding:utf-8-*-

from dao.mongotool import *


class UserInfo(Table):
    __table__ = 'userinfo'
    game_id = AssistColumnClass(int)
    expire_time = AssistColumnClass(int)
    last_login_time = AssistColumnClass(int)
    login_times = AssistColumnClass(int)
    register_time = AssistColumnClass(int)
    cd_key_info = AssistColumnClass()

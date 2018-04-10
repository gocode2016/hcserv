# -*-coding:utf-8-*-

import hashlib
from serv.serv_base import app
from flask import request
from wx.handles import *
from wx.tools import *


@app.route('/hcserv/wx')
def wx_verify():
    """
    验证服务器信息
    :return:
    """
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')
    token = config['wx_token']
    if None in [signature, timestamp, nonce, echostr, token]:
        return "--"
    ls = [token, timestamp, nonce]
    ls.sort()
    sha1 = hashlib.sha1()
    for s in ls:
        sha1.update(s.encode('utf-8'))
    hashcode = sha1.hexdigest()
    if hashcode == signature:
        return echostr
    else:
        return ""


@app.route('/hcserv/wx', methods=['post'])
def wx_reply():
    """
    公众号实际消息处理
    :return:
    """
    data = request.data
    message = parse_wx_message(data)
    if message is None:
        return ""

    user_id = message[FromUserName]
    self_id = message[ToUserName]
    receive = message[Content]

    # 如果是一个指令，就调用awake方法
    if receive in instruct_awake_func:
        # 如果输的是指令，就把指令存入到redis中
        redis_client.delete(user_id)
        redis_client.hset(user_id, "instruct", receive)
        # 两分钟后过期
        redis_client.expire(user_id, 120)
        return build_wx_response_xml_b(
            user_id,
            self_id,
            instruct_awake_func[receive]()
        )

    user_input_before = redis_client.hgetall(user_id)
    # data_before如果是None/0/False就返回None,不是的话就返回后面的
    # 这里有坑。。。{}空字典也是作为False来处理的。。。（包含所有为空的集合
    instruct = user_input_before and user_input_before.get("instruct")
    logging.info(instruct)

    # 如果缓存中存在已经输入过的合法指令，就调用相关handle处理
    if instruct:
        return build_wx_response_xml_b(
            user_id,
            self_id,
            instruct_handles_func[instruct](
                user_id,
                receive,
                user_input_before
            )
        )

    # 如果是瞎几把输入的值，提示可以选择的输入选项
    return build_wx_response_xml_b(
        user_id,
        self_id,
        "请输入数字来使用相关功能：\n1 ) 使用cdkey"
    )

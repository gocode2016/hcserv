import re
from datetime import datetime

_get_text_message_pattern = re.compile(
    r'<xml><ToUserName><!\[CDATA\[(.*?)\]\]></ToUserName>\n'
    r'<FromUserName><!\[CDATA\[(.*?)\]\]></FromUserName>\n'
    r'<CreateTime>(.*?)</CreateTime>\n'
    r'<MsgType><!\[CDATA\[text\]\]></MsgType>\n'
    r'<Content><!\[CDATA\[(.*?)\]\]></Content>\n'
    r'<MsgId>(.*?)</MsgId>\n</xml>')

_send_text_message_pattern = (
    '<xml>\n'
    '<ToUserName><![CDATA[%s]]></ToUserName>\n'
    '<FromUserName><![CDATA[%s]]></FromUserName>\n'
    '<CreateTime>%s</CreateTime>\n'
    '<MsgType><![CDATA[text]]></MsgType>\n'
    '<Content><![CDATA[%s]]></Content>\n'
    '</xml>'
)

ToUserName = 'ToUserName'
FromUserName = 'FromUserName'
CreateTime = 'CreateTime'
Content = 'Content'
MsgId = 'MsgId'


def parse_wx_message(message: bytes):
    message = message.decode('utf-8')
    match = _get_text_message_pattern.match(message)
    if match:
        return {
            ToUserName: match.group(1),
            FromUserName: match.group(2),
            CreateTime: match.group(3),
            Content: match.group(4),
            MsgId: match.group(5),
        }
    return None


def build_wx_response_xml_b(to, from_, content) -> bytes:
    return (
        _send_text_message_pattern % (
            to,
            from_,
            str(int(datetime.now().timestamp())),
            content,
        )
    ).encode('utf-8')

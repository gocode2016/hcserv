# -*- coding:utf-8-*-
import redis
from config.config import config

# 因为这里用的是多个单线程的进程起的服务器，因此连接池应该是不需要的
# _pool = redis.Connection(
#     host=config['redis_host'],
#     port=6379,
#     decode_responses=True
# )

password = config.get('redis_pswd')
redis_client = redis.Redis(
    host=config['redis_host'],
    port=6379,
    decode_responses=True,
) if password else redis.Redis(
    host=config['redis_host'],
    port=6379,
    decode_responses=True,
    password=password
)

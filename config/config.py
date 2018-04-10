# -*- coding:utf-8 -*-

# 线上环境配置写到config_online.py中
# 本地开发环境配置写到config_dev.py中
# config_dev.py 覆盖 config_online.py 覆盖 config.py
# 该文件下的config中的值仅仅用来占位，方便IDE做提示
config = {
    'db_host': 'localhost',
    'redis_host': 'localhost',
    'db_name': 'localhost',
    'server_host': 'localhost',
    'server_user': 'localhost',
    'server_pswd': 'localhost',
    'wx_token': 'localhost',
    'redis_pswd': '',
    'wx_admin_pswd': '',
}


def config_merge(base_: dict, override: dict):
    """
    将overrid里面的值覆盖base_里的值，以达到配置合并的效果

    :param base_: 基础配置
    :param override: 需要覆盖基础配置的配置
    :return: 无返回值
    """
    for k, v in override.items():
        if k not in base_ or type(v) is not dict:
            # 递归基
            # 如果基础配置里没有这个键，或值不是字典类型
            # 直接把该键存下来或覆盖写入
            base_[k] = v
        else:
            # 如果这个键对应的值是且已存在字典，递归的合并
            config_merge(base_[k], v)


# 使用线上配置覆盖默认配置
try:
    # 如果有这个模块的话，将其中的配置读入
    from config.config_online import config as _config
    config_merge(config, _config)
except ModuleNotFoundError as ignore:
    pass

# 使用本地开发环境覆盖线上配置
# 在本地开发的时候，三个配置文件都有，因此用开发配置去覆盖其他的配置
# 在传到线上的时候，config_dev是不存在的，因此线上配置也就不会被覆盖了
try:
    # 如果有这个模块的话，将其中的配置读入
    from config.config_dev import config as _config
    config_merge(config, _config)
except ModuleNotFoundError as ignore:
    pass

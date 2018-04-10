# -*-coding:utf-8-*-

from fabric.api import *
from config.config import config
from datetime import datetime

env.hosts = [config['server_host']]
env.user = config['server_user']
env.password = config['server_pswd']

_TAR_FILE = 'hc_script_serv.tar.gz'


def build():
    """
    打包本地的工程项目到 dist/_TAR_FILE中
    :return:
    """
    includes = ['*.sh', '*.py', 'dao', 'utils', 'config', 'wx', 'serv']
    excludes = ['dist', 'myunittest', 'test', 'config_dev.py']
    local('rm -f dist/%s' % _TAR_FILE)
    cmd = ['tar', '--dereference', '-czvf', 'dist/%s' % _TAR_FILE]
    cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
    cmd.extend(includes)
    local(' '.join(cmd))


_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/home/yang/code/python/hcserv'


def deploy():
    newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    # 删除已有的tar文件:
    run('rm -f %s' % _REMOTE_TMP_TAR)
    # 上传新的tar文件:
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    # 创建新目录:
    with cd(_REMOTE_BASE_DIR):
        run('mkdir %s' % newdir)
    # 解压到新目录:
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        run('tar -xzvf %s' % _REMOTE_TMP_TAR)
    # 重置软链接:
    with cd(_REMOTE_BASE_DIR):
        run('rm -f www')
        run('ln -s %s www' % newdir)
        run('chmod +x www/start.sh')
        # sudo('chown www-data:www-data www')
        # sudo('chown -R www-data:www-data %s' % newdir)
    # 重启Python服务和nginx服务器:
    with settings(warn_only=True):
        sudo('supervisorctl stop hc_serv')
        sudo('supervisorctl start hc_serv')
        sudo('/etc/init.d/nginx reload')

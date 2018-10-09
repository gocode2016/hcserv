#!/usr/bin/env bash

# `/Users/yang/anaconda3/envs/py36web` 这部分修改本机对应的环境
export PATH="/home/yang/Applications/anaconda3/envs/py36web/bin:${PATH}"
exec gunicorn -k gevent --worker-connections 10 -b 127.0.0.1:30000 -w 3 start:app

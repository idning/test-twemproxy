#!/usr/bin/env python
#coding: utf-8

import os
import sys
import redis

PWD = os.path.dirname(os.path.realpath(__file__))
WORKDIR = os.path.join(PWD,  '../')
sys.path.append(os.path.join(WORKDIR, 'lib/'))
sys.path.append(os.path.join(WORKDIR, 'conf/'))
import conf

from server_modules import *
from utils import *


CLUSTER_NAME = 'ttt'

all_redis = [
        RedisServer('127.0.0.5', 2100, '/tmp/r/redis-2100/', CLUSTER_NAME, 'redis-2100'),
        RedisServer('127.0.0.5', 2101, '/tmp/r/redis-2101/', CLUSTER_NAME, 'redis-2101'),
    ]

def setup():
    for r in all_redis:
        r.deploy()
        r.start()

    nc = NutCracker('127.0.0.5', 4100, '/tmp/r/nutcracker-4100/', CLUSTER_NAME, all_redis)
    nc.deploy()
    nc.start()

def test_multi_delete_on_readonly():
    all_redis[0].slaveof(all_redis[1].args['host'], all_redis[1].args['port'])

    conn = redis.Redis('127.0.0.5', 4100)

    assert_fail('READONLY', conn.delete, 'key-1')           # got "READONLY You can't write against a read only slave"
    assert_equal(0, conn.delete('key-2'))
    assert_fail('READONLY', conn.delete, 'key-3')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Invalid argument', conn.delete, *keys)     # got "Invalid argument"

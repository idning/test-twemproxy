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

######################################################

CLUSTER_NAME = 'ttt'

all_redis = [
        RedisServer('127.0.0.5', 2100, '/tmp/r/redis-2100', CLUSTER_NAME, 'redis-2100'),
        RedisServer('127.0.0.5', 2101, '/tmp/r/redis-2101', CLUSTER_NAME, 'redis-2101'),
    ]

nc = NutCracker('127.0.0.5', 4100, '/tmp/r/nutcracker-4100', CLUSTER_NAME, all_redis)

def setup():
    for r in all_redis:
        r.deploy()
        r.stop()
        r.start()

    nc.deploy()
    nc.stop()
    nc.start()

def teardown():
    for r in all_redis:
        r.stop()
    nc.stop()

######################################################

def test_mget_mset(cnt=10):
    conn = redis.Redis(nc.host(), nc.port())

    def insert_by_pipeline():
        pipe = conn.pipeline(transaction=False)
        for i in range(cnt):
            pipe.set('kkk-%s'%i, 'vvv-%s'%i)
        pipe.execute()

    def insert_by_mset():
        kv = {'kkk-%s' % i :'vvv-%s' % i for i in range(cnt)}
        ret = conn.mset(**kv)

    try:
        insert_by_mset() #only the mget-imporve branch support this
    except:
        insert_by_pipeline()
    keys = ['kkk-%s' % i for i in range(cnt)]

    #mget to check
    vals = conn.mget(keys)
    for i in range(cnt):
        assert('vvv-%s'%i == vals[i])

    #del
    assert (cnt == conn.delete(*keys) )

    #mget again
    vals = conn.mget(keys)
    for i in range(cnt):
        assert(None == vals[i])

def test_mget_mset_large():
    for i in range(1, 10000, 171):
        test_mget_mset(i)


def test_mget_binary_value(cnt=5):
    conn = redis.Redis(nc.host(), nc.port())
    kv = {}
    for i in range(cnt):
        kv['kkx-%s' % i] = os.urandom(1024*1024*8)

    ret = conn.mset(**kv)

    keys = ['kkx-%s' % i for i in range(cnt)]

    #mget to check
    vals = conn.mget(keys)
    for i in range(cnt):
        key = 'kkx-%s' % i
        assert(kv[key] == vals[i])

def _test_mget_on_backend_down():
    #one backend down
    all_redis[0].stop()
    conn = redis.Redis(nc.host(), nc.port())

    assert_fail('Connection refused', conn.delete, 'key-1')
    assert_equal(None, conn.get('key-2'))

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused', conn.delete, *keys)

    #all backend down
    all_redis[1].stop()
    conn = redis.Redis('127.0.0.5', 4100)

    assert_fail('Connection refused', conn.delete, 'key-1')
    assert_fail('Connection refused', conn.delete, 'key-2')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused', conn.delete, *keys)


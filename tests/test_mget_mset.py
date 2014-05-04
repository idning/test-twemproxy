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

if 'NC_VERBOSE' in os.environ:
    nc_verbose = os.environ['NC_VERBOSE']
else:
    nc_verbose = 4

nc = NutCracker('127.0.0.5', 4100, '/tmp/r/nutcracker-4100', CLUSTER_NAME, all_redis, verbose=nc_verbose)

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
    assert(nc._alive())
    nc.stop()

######################################################

default_kv = {'kkk-%s' % i :'vvv-%s' % i for i in range(10)}
def test_mget_mset(kv=default_kv):
    conn = redis.Redis(nc.host(), nc.port())

    def insert_by_pipeline():
        pipe = conn.pipeline(transaction=False)
        for k, v in kv.items():
            pipe.set(k, v)
        pipe.execute()

    def insert_by_mset():
        ret = conn.mset(**kv)

    insert_by_mset() #only the mget-imporve branch support this
    #try:
        #insert_by_mset() #only the mget-imporve branch support this
    #except:
        #insert_by_pipeline()

    keys = kv.keys()

    #mget to check
    vals = conn.mget(keys)
    for i, k in enumerate(keys):
        assert(kv[k] == vals[i])

    #del
    assert (len(keys) == conn.delete(*keys) )

    #mget again
    vals = conn.mget(keys)

    for i, k in enumerate(keys):
        assert(None == vals[i])

def test_mget_mset_large():
    for cnt in range(1, 1000, 171):
        kv = {'kkk-%s' % i :'vvv-%s' % i for i in range(cnt)}
        test_mget_mset(kv)

def test_mget_special_key(cnt=5):
    #key length = 512-48
    kv = {}
    for i in range(cnt):
        k = 'kkk-%s' % i
        k = k + 'x'*(512-48-1-len(k))
        kv[k] = 'vvv'

    test_mget_mset(kv)

def test_mget_on_backend_down():
    #one backend down
    all_redis[0].stop()
    conn = redis.Redis(nc.host(), nc.port())

    assert_fail('Connection refused|reset by peer', conn.mget, 'key-1')
    assert_equal(None, conn.get('key-2'))

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', conn.mget, *keys)

    #all backend down
    all_redis[1].stop()
    conn = redis.Redis('127.0.0.5', 4100)

    assert_fail('Connection refused|reset by peer', conn.mget, 'key-1')
    assert_fail('Connection refused|reset by peer', conn.mget, 'key-2')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', conn.mget, *keys)


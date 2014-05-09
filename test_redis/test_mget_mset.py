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

nc_verbose = int(getenv('NC_VERBOSE', 4))
mbuf = int(getenv('NC_MBUF', 512))
large = int(getenv('NC_LARGE', 1000))

nc = NutCracker('127.0.0.5', 4100, '/tmp/r/nutcracker-4100', CLUSTER_NAME, all_redis, mbuf=mbuf, verbose=nc_verbose)

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

def test_mget_mset_on_key_not_exist(kv=default_kv):
    conn = redis.Redis(nc.host(), nc.port())

    def insert_by_pipeline():
        pipe = conn.pipeline(transaction=False)
        for k, v in kv.items():
            pipe.set(k, v)
        pipe.execute()

    def insert_by_mset():
        ret = conn.mset(**kv)

    try:
        insert_by_mset() #only the mget-imporve branch support this
    except:
        insert_by_pipeline()

    keys = kv.keys()
    keys2 = ['x-'+k for k in keys]
    keys = keys + keys2
    random.shuffle(keys)

    #mget to check
    vals = conn.mget(keys)
    for i, k in enumerate(keys):
        if k in kv:
            assert(kv[k] == vals[i])
        else:
            assert(vals[i] == None)

    #del
    assert (len(kv) == conn.delete(*keys) )

    #mget again
    vals = conn.mget(keys)

    for i, k in enumerate(keys):
        assert(None == vals[i])

def test_mget_mset_large():
    for cnt in range(171, large, 171):
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

def test_mget_special_key_2(cnt=5):
    #key length = 512-48
    kv = {}
    for i in range(cnt):
        k = 'kkk-%s' % i
        k = k + 'x'*(512-48-2-len(k))
        kv[k] = 'vvv'*9

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

def test_mset_on_backend_down():
    all_redis[0].stop()
    conn = redis.Redis(nc.host(),nc.port())

    assert_fail('Connection refused',conn.mset,default_kv)

    all_redis[1].stop()
    assert_fail('Connection refused',conn.mset,default_kv)

    
def test_mget_pipeline():
    conn = redis.Redis(nc.host(),nc.port())
    pipe = conn.pipeline(transaction=False)
    for k,v in default_kv.items():
        pipe.set(k,v)
    keys = default_kv.keys()
    pipe.mget(keys)
    kv = {}
    for i in range(10000):
        kv['kkk-%s' % i] = os.urandom(100)
    for k,v in kv.items():
        pipe.set(k,v)
    for k in kv.keys():
        pipe.get(k)
    pipe.execute()

    #check the result
    keys = default_kv.keys()

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


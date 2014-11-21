#!/usr/bin/env python
#coding: utf-8

from common import *

all_redis = [
        RedisServer('127.0.0.5', 2100, '/tmp/r/redis-2100/', CLUSTER_NAME, 'redis-2100', auth = 'hellopasswd'),
        RedisServer('127.0.0.5', 2101, '/tmp/r/redis-2101/', CLUSTER_NAME, 'redis-2101', auth = 'hellopasswd'),
        ]

nc = NutCracker('127.0.0.5', 4100, '/tmp/r/nutcracker-4100', CLUSTER_NAME, all_redis, mbuf=mbuf, verbose=nc_verbose, redis_auth = 'hellopasswd')

def setup():
    print 'setup(mbuf=%s, verbose=%s)' %(mbuf, nc_verbose)
    for r in all_redis + [nc]:
        r.deploy()
        r.stop()
        r.start()

def teardown():
    for r in all_redis + [nc]:
        assert(r._alive())
        r.stop()
        if clean:
            r.clean()

default_kv = {'kkk-%s' % i : 'vvv-%s' % i for i in range(10)}

def getconn():
    for r in all_redis:
        c = redis.Redis(r.host(), r.port())
        c.flushdb()

    r = redis.Redis(nc.host(), nc.port())
    return r

def test_setget():
    r = getconn()

    rst = r.set('k', 'v')
    assert(r.get('k') == 'v')

def setup_and_wait():
    time.sleep(60*60)

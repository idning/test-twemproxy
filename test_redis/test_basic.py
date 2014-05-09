#!/usr/bin/env python
#coding: utf-8

import os
import sys
import redis

PWD = os.path.dirname(os.path.realpath(__file__))
WORKDIR = os.path.join(PWD,'../')
sys.path.append(os.path.join(WORKDIR,'lib/'))
sys.path.append(os.path.join(WORKDIR,'conf/'))

import conf

from server_modules import *
from utils import *

CLUSTER_NAME = 'ttt'
all_redis = [
        RedisServer('127.0.0.5', 2100, '/tmp/r/redis-2100/', CLUSTER_NAME, 'redis-2100'),
        RedisServer('127.0.0.5', 2101, '/tmp/r/redis-2101/', CLUSTER_NAME, 'redis-2101'),
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

default_kv = {'kkk-%s' % i : 'vvv-%s' % i for i in range(10)}
def test_zadd():
    conn = redis.Redis('127.0.0.5',4100)
    rst = conn.zadd('z', 'z1', 1)
    # should return 1 but actual return 0
    print rst
                        
def test_msetnx():
    conn = redis.Redis("127.0.0.5",4100);
    keys = default_kv.keys()
    #rst = conn.msetnx(**default_kv) 
    
    assert_fail('Socket closed', conn.msetnx,**default_kv)

def test_lpush_lrange():
    conn = redis.Redis("127.0.0.5",4100);
    vals = ['vvv-%s' % i for i in range(10) ]
    conn.delete('mylist')
    assert [] == conn.lrange('mylist', 0, -1)
    
    conn.lpush('mylist', *vals)
    rst = conn.lrange('mylist', 0, -1)
    
    assert 10 == len(rst)


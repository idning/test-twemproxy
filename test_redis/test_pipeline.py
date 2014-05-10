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

def test_pipeline():
    conn = redis.Redis('127.0.0.5',4100)
    pipe = conn.pipeline(transaction=False)
    pipe.set('a','a1').get('a')
#zadd return result is not the same as from redis-cli,maybe redis-py problem
#.zadd('z', 'z1', 1).zadd('z', 'z2', 4)
#    pipe.zincrby('z','z1').zrange('z',0,5,withscores=True)
    rst = pipe.execute()

    assert rst == [True, 'a1']
                        
def test_pipeline_length():
    conn = redis.Redis('127.0.0.5',4100)
    pipe = conn.pipeline(transaction = False)
    assert len(pipe) == 0
    assert not pipe

    pipe.set('a','a1').set('b','b1').set('c','c1')
    assert len(pipe) == 3
    assert pipe

    pipe.execute()
    assert len(pipe) == 0
    assert not pipe





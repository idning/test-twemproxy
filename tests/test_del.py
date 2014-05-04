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

def test_multi_delete_normal():
    conn = redis.Redis('127.0.0.5', 4100)
    for i in range(100):
        conn.set('key-%s'%i, 'val-%s'%i)
    for i in range(100):
        assert_equal('val-%s'%i, conn.get('key-%s'%i) )

    keys = ['key-%s'%i for i in range(100)]
    assert_equal(100, conn.delete(*keys))

    for i in range(100):
        assert_equal(None, conn.get('key-%s'%i) )

def test_multi_delete_on_readonly():
    all_redis[0].slaveof(all_redis[1].args['host'], all_redis[1].args['port'])

    conn = redis.Redis('127.0.0.5', 4100)

    assert_fail('READONLY|Invalid', conn.delete, 'key-1')           # got "READONLY You can't write against a read only slave"
    assert_equal(0, conn.delete('key-2'))
    assert_fail('READONLY|Invalid', conn.delete, 'key-3')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Invalid argument', conn.delete, *keys)     # got "Invalid argument"

def test_multi_delete_on_backend_down():
    #one backend down
    all_redis[0].stop()
    conn = redis.Redis('127.0.0.5', 4100)

    assert_fail('Connection refused|reset by peer', conn.delete, 'key-1')
    assert_equal(None, conn.get('key-2'))

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', conn.delete, *keys)

    #all backend down
    all_redis[1].stop()
    conn = redis.Redis('127.0.0.5', 4100)

    assert_fail('Connection refused|reset by peer', conn.delete, 'key-1')
    assert_fail('Connection refused|reset by peer', conn.delete, 'key-2')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', conn.delete, *keys)


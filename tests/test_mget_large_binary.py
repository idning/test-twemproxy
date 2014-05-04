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

nc = NutCracker('127.0.0.5', 4100, '/tmp/r/nutcracker-4100', CLUSTER_NAME, all_redis, verbose=nc_verbose, mbuf=16*1024)

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

from test_mget_mset import test_mget_mset
######################################################

def test_mget_binary_value(cnt=5):
    kv = {}
    for i in range(cnt):
        kv['kkk-%s' % i] = os.urandom(1024*1024*16+1024)
    for i in range(cnt):
        kv['kkk2-%s' % i] = ''
    test_mget_mset(kv)


#!/usr/bin/env python
#coding: utf-8

import os
import sys
import redis
import memcache

PWD = os.path.dirname(os.path.realpath(__file__))
WORKDIR = os.path.join(PWD,  '../')
sys.path.append(os.path.join(WORKDIR, 'lib/'))
sys.path.append(os.path.join(WORKDIR, 'conf/'))
import conf

from server_modules import *
from utils import *

######################################################


CLUSTER_NAME = 'ttt'
all_mc= [
        Memcached('127.0.0.5', 2200, '/tmp/r/memcached-2200/', CLUSTER_NAME, 'mc-2200'),
        Memcached('127.0.0.5', 2201, '/tmp/r/memcached-2201/', CLUSTER_NAME, 'mc-2201'),
    ]

if 'NC_VERBOSE' in os.environ:
    nc_verbose = os.environ['NC_VERBOSE']
else:
    nc_verbose = 4

nc = NutCracker('127.0.0.5', 4100, '/tmp/r/nutcracker-4100', CLUSTER_NAME, all_mc, verbose=nc_verbose, is_redis=False)

def setup():
    for r in all_mc:
        r.deploy()
        r.stop()
        r.start()

    nc.deploy()
    nc.stop()
    nc.start()

def teardown():
    for r in all_mc:
        r.stop()
    assert(nc._alive())
    nc.stop()
    pass

######################################################

def test_basic():
    mc = memcache.Client(['127.0.0.1:4100'])
    mc.set('k', 'v')
    assert('v' == mc.get('k'))


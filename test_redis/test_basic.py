#!/usr/bin/env python
#coding: utf-8

from common import *

def test_setget():
    conn = redis.Redis('127.0.0.5',4100)
    rst = conn.set('k', 'v')
    assert(conn.get('k'), 'v')

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

def test_fuzz():
    conn = redis.Redis(nc.host(),nc.port())
    #not supported
    assert_fail('Socket closed', conn.msetnx, **default_kv)

def test_slow_req():
    conn = redis.Redis(nc.host(),nc.port())
    kv = {'mkkk-%s' % i : 'mvvv-%s' % i for i in range(300000)}

    pipe = conn.pipeline(transaction=False)
    pipe.set('key-1', 'v1')
    pipe.get('key-1')
    pipe.hmset('xxx', kv)
    pipe.get('key-2')
    pipe.get('key-3')

    assert_fail('timed out', pipe.execute)

def test_signal():
    #init
    nc.cleanlog()
    nc.signal('HUP')

    nc.signal('HUP')
    nc.signal('TTIN')
    nc.signal('TTOU')
    nc.signal('SEGV')
    log = file(nc.logfile()).read()

    assert(strstr(log, 'HUP'))
    assert(strstr(log, 'TTIN'))
    assert(strstr(log, 'TTOU'))
    assert(strstr(log, 'SEGV'))

    #recover
    nc.start()

def setup_and_wait():
    time.sleep(60*60)

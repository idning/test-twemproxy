#!/usr/bin/env python
#coding: utf-8

from common import *

def test_zadd():
    conn = redis.Redis('127.0.0.5',4100)
    rst = conn.zadd('z', 'z1', 1)
    # should return 1 but actual return 0
    #print rst

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

#!/usr/bin/env python
#coding: utf-8

from common import *

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


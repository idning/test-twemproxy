#!/usr/bin/env python
#coding: utf-8

from common import *

def test_multi_delete_normal():
    r = getconn()

    for i in range(100):
        r.set('key-%s'%i, 'val-%s'%i)
    for i in range(100):
        assert_equal('val-%s'%i, r.get('key-%s'%i) )

    keys = ['key-%s'%i for i in range(100)]
    assert_equal(100, r.delete(*keys))

    for i in range(100):
        assert_equal(None, r.get('key-%s'%i) )

def test_multi_delete_on_readonly():
    all_redis[0].slaveof(all_redis[1].args['host'], all_redis[1].args['port'])

    r = redis.Redis(nc.host(), nc.port())

    assert_fail('READONLY|Invalid', r.delete, 'key-1')           # got "READONLY You can't write against a read only slave"
    assert_equal(0, r.delete('key-2'))
    assert_fail('READONLY|Invalid', r.delete, 'key-3')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Invalid argument', r.delete, *keys)     # got "Invalid argument"

def test_multi_delete_on_backend_down():
    #one backend down
    all_redis[0].stop()
    r = redis.Redis(nc.host(), nc.port())

    assert_fail('Connection refused|reset by peer', r.delete, 'key-1')
    assert_equal(None, r.get('key-2'))

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', r.delete, *keys)

    #all backend down
    all_redis[1].stop()
    r = redis.Redis(nc.host(), nc.port())

    assert_fail('Connection refused|reset by peer', r.delete, 'key-1')
    assert_fail('Connection refused|reset by peer', r.delete, 'key-2')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', r.delete, *keys)

    for r in all_redis:
        r.start()


def test_multi_delete_20140525():
    r = getconn()

    cnt = 126
    keys = ['key-%s'%i for i in range(cnt)]
    pipe = r.pipeline(transaction=False)
    pipe.mget(keys)
    pipe.delete(*keys)
    pipe.execute()



#!/usr/bin/env python
#coding: utf-8

from common import *

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

    for r in all_redis:
        r.start()


def test_multi_delete_20140525():
    conn = redis.Redis('127.0.0.5', 4100)
    cnt = 126
    keys = ['key-%s'%i for i in range(cnt)]
    pipe = conn.pipeline(transaction=False)
    pipe.mget(keys)
    pipe.delete(*keys)
    print pipe.execute()



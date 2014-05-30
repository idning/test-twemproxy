#!/usr/bin/env python
#coding: utf-8

from common import *

def test_mget_mset(kv=default_kv):
    conn = redis.Redis(nc.host(), nc.port())

    def insert_by_pipeline():
        pipe = conn.pipeline(transaction=False)
        for k, v in kv.items():
            pipe.set(k, v)
        pipe.execute()

    def insert_by_mset():
        ret = conn.mset(**kv)

    #insert_by_mset() #only the mget-imporve branch support this
    try:
        insert_by_mset() #only the mget-imporve branch support this
    except:
        insert_by_pipeline()

    keys = kv.keys()

    #mget to check
    vals = conn.mget(keys)
    for i, k in enumerate(keys):
        assert(kv[k] == vals[i])

    #del
    assert (len(keys) == conn.delete(*keys) )

    #mget again
    vals = conn.mget(keys)

    for i, k in enumerate(keys):
        assert(None == vals[i])

def test_mget_mset_on_key_not_exist(kv=default_kv):
    conn = redis.Redis(nc.host(), nc.port())

    def insert_by_pipeline():
        pipe = conn.pipeline(transaction=False)
        for k, v in kv.items():
            pipe.set(k, v)
        pipe.execute()

    def insert_by_mset():
        ret = conn.mset(**kv)

    try:
        insert_by_mset() #only the mget-imporve branch support this
    except:
        insert_by_pipeline()

    keys = kv.keys()
    keys2 = ['x-'+k for k in keys]
    keys = keys + keys2
    random.shuffle(keys)

    #mget to check
    vals = conn.mget(keys)
    for i, k in enumerate(keys):
        if k in kv:
            assert(kv[k] == vals[i])
        else:
            assert(vals[i] == None)

    #del
    assert (len(kv) == conn.delete(*keys) )

    #mget again
    vals = conn.mget(keys)

    for i, k in enumerate(keys):
        assert(None == vals[i])

def test_mget_mset_large():
    for cnt in range(171, large, 171):
        kv = {'kkk-%s' % i :'vvv-%s' % i for i in range(cnt)}
        test_mget_mset(kv)

def test_mget_special_key(cnt=5):
    #key length = 512-48-1
    kv = {}
    for i in range(cnt):
        k = 'kkk-%s' % i
        k = k + 'x'*(512-48-1-len(k))
        kv[k] = 'vvv'

    test_mget_mset(kv)

def test_mget_special_key_2(cnt=5):
    #key length = 512-48-2
    kv = {}
    for i in range(cnt):
        k = 'kkk-%s' % i
        k = k + 'x'*(512-48-2-len(k))
        kv[k] = 'vvv'*9

    test_mget_mset(kv)

def test_fuzz():
    conn = redis.Redis(nc.host(),nc.port())
    #not supported
    assert_fail('Socket closed', conn.msetnx, **default_kv)

def test_nc_stats():
    nc.stop() #reset counters
    nc.start()
    conn = redis.Redis(nc.host(),nc.port())
    kv = {'kkk-%s' % i :'vvv-%s' % i for i in range(10)}
    for k, v in kv.items():
        conn.set(k, v)
        conn.get(k)

    def get_stat(name):
        time.sleep(1)
        stat = nc._info_dict()
        #pprint(stat)
        if name in [ 'client_connections', 'client_eof', 'client_err', 'forward_error', 'fragments', 'server_ejects']:
            return stat[CLUSTER_NAME][name]

        #sum num of each server
        ret = 0
        for k, v in stat[CLUSTER_NAME].items():
            if type(v) == dict:
                ret += v[name]
        return ret

    assert(get_stat('requests') == 20)
    assert(get_stat('responses') == 20)

    ##### mget
    keys = kv.keys()
    conn.mget(keys)

    #for version<=0.3.0
    #assert(get_stat('requests') == 30)
    #assert(get_stat('responses') == 30)

    #for mget-improve
    assert(get_stat('requests') == 22)
    assert(get_stat('responses') == 22)

def test_mget_on_backend_down():
    #one backend down
    all_redis[0].stop()
    conn = redis.Redis(nc.host(), nc.port())

    assert_fail('Connection refused|reset by peer', conn.mget, 'key-1')
    assert_equal(None, conn.get('key-2'))

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', conn.mget, *keys)

    #all backend down
    all_redis[1].stop()
    conn = redis.Redis('127.0.0.5', 4100)

    assert_fail('Connection refused|reset by peer', conn.mget, 'key-1')
    assert_fail('Connection refused|reset by peer', conn.mget, 'key-2')

    keys = ['key-1', 'key-2', 'kkk-3']
    assert_fail('Connection refused|reset by peer', conn.mget, *keys)

    for r in all_redis:
        r.start()

def test_mset_on_backend_down():
    all_redis[0].stop()
    conn = redis.Redis(nc.host(),nc.port())

    assert_fail('Connection refused',conn.mset,default_kv)

    all_redis[1].stop()
    assert_fail('Connection refused',conn.mset,default_kv)

    for r in all_redis:
        r.start()

def test_mget_pipeline():
    conn = redis.Redis(nc.host(),nc.port())
    pipe = conn.pipeline(transaction=False)
    for k,v in default_kv.items():
        pipe.set(k,v)
    keys = default_kv.keys()
    pipe.mget(keys)
    kv = {}
    for i in range(large):
        kv['kkk-%s' % i] = os.urandom(100)
    for k,v in kv.items():
        pipe.set(k,v)
    for k in kv.keys():
        pipe.get(k)
    rst = pipe.execute()

    #print rst
    #check the result
    keys = default_kv.keys()

    #mget to check
    vals = conn.mget(keys)
    for i, k in enumerate(keys):
        assert(kv[k] == vals[i])

    #del
    assert (len(keys) == conn.delete(*keys) )

    #mget again
    vals = conn.mget(keys)

    for i, k in enumerate(keys):
        assert(None == vals[i])


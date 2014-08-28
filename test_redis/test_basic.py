#!/usr/bin/env python
#coding: utf-8

from common import *

def test_setget():
    r = getconn()
    rst = r.set('k', 'v')
    assert(r.get('k') == 'v')

def test_msetnx():
    r = getconn()
    keys = default_kv.keys()
    #rst = r.msetnx(**default_kv)

    assert_fail('Socket closed', r.msetnx,**default_kv)

def test_fuzz():
    r = getconn()
    #not supported
    assert_fail('Socket closed', r.msetnx, **default_kv)

def test_slow_req():
    r = getconn()
    kv = {'mkkk-%s' % i : 'mvvv-%s' % i for i in range(300000)}

    pipe = r.pipeline(transaction=False)
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
    time.sleep(.3)
    log = file(nc.logfile()).read()

    assert(strstr(log, 'HUP'))
    assert(strstr(log, 'TTIN'))
    assert(strstr(log, 'TTOU'))
    assert(strstr(log, 'SEGV'))

    #recover
    nc.start()

def setup_and_wait():
    time.sleep(60*60)

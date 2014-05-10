Python testing facilities for twemproxy, this test suite is based on https://github.com/idning/redis-mgr

usage
=====

1. install dependency::

    pip install nose
    pip install redis
    pip install -e git://github.com/idning/python-memcached.git#egg=memcache

2. copy binarys to _binaries/::

    _binaries/
    |-- nutcracker
    |-- redis-benchmark
    |-- redis-check-aof
    |-- redis-check-dump
    |-- redis-cli
    |-- redis-sentinel
    |-- redis-server
    |-- memcached

3. run::

    $ nosetests -v
    test_del.test_multi_delete_on_readonly ... ok
    test_mget.test_mget ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 4.483s

    OK

4. add A case::

    cp tests/test_del.py tests/test_xxx.py
    vim tests/test_xxx.py


variables
=========
::

    export NC_VERBOSE=9 will start nutcracker with '-v 9'  (default:4)
    export NC_MBUF=512  will start nutcracker whit '-m 512' (default:521)
    export NC_LARGE=10000 will test 10000 keys for mget/mset (default:1000)



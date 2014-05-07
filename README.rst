Python testing facilities for twemproxy

usage
=====

1. install dependency::

    pip install nose
    pip install redis
    git clone https://github.com/idning/python-memcached
    cd python-memcached && python setup.py install

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


debug
=====

export NC_VERBOSE=9


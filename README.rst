test-twemproxy
##############

dependency:

- redis-py
- nosetests

usage:

1. copy binarys to _binaries/::

    _binaries/
    |-- nutcracker
    |-- redis-benchmark
    |-- redis-check-aof
    |-- redis-check-dump
    |-- redis-cli
    |-- redis-sentinel
    `-- redis-server

2. run::

    nosetests

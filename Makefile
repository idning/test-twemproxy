all:
	nosetests --nocapture  --nologcapture -v
	
debug:
	export NC_VERBOSE=9; nosetests --nocapture  --nologcapture -v

large:
	export NC_LARGE=10000; nosetests --nocapture  --nologcapture -v

one:
	nosetests --nocapture --nologcapture -v test_redis/test_del.py:test_multi_delete_20140525

wait:
	nosetests --nocapture --nologcapture -v test_redis/test_basic.py:setup_and_wait


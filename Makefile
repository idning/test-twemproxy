all:
	nosetests --nocapture  --nologcapture -v
	
debug:
	export NC_VERBOSE=9
	nosetests --nocapture  --nologcapture -v

one:
	nosetests --nocapture --nologcapture -v test_redis/test_del.py:test_multi_delete_20140525

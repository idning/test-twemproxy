
NOSE=nosetests --nologcapture -x 

all:
	$(NOSE) -v
	
debug:
	export T_VERBOSE=9; $(NOSE) -v

large:
	export T_LARGE=10000; $(NOSE)

one:
	$(NOSE) test_redis/test_del.py:test_multi_delete_20140525

wait:
	$(NOSE) -v test_redis/test_basic.py:setup_and_wait

clean:
	find . -name '*.pyc' | xargs rm -f
	rm gmon.out *.log


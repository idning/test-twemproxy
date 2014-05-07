all:
	nosetests --nocapture  --nologcapture -v
	
debug:
	export NC_VERBOSE=9
	nosetests --nocapture  --nologcapture -v



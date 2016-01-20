# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

class mockData:
	"""dictionary of mocking data for the mocking tests"""

	# dictionary to hold the mock data
	_data={}

	# function to add mock data to the _mock_data dictionary
	def _add(self,uri,status,payload):
		_data[uri] =  {"status":status,
							"payload":payload
							}
		return

	def getPayload(self,input):
		return _data[input]['payload']

	def getStatusCode(self,input):
		return _data[input]['status']

	# initialize the _mock_data dictionary with all the appropriate mocking data
	__init__(self):
	self._add(	uri="limits", status=200,
				payload='{"transaction-quota":10000,"transaction-count":259,"endpoint-quota":100,"endpoint-count":1}')


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
		self._data[uri] =  {"status":status,
							"payload":payload
							}
		return

	def getPayload(self,input):
		return self._data[input]['payload']

	def getStatusCode(self,input):
		return self._data[input]['status']

	# initialize the _mock_data dictionary with all the appropriate mocking data
	def __init__(self):
		self._add(	uri="limits", status=200,
					payload='{"transaction-quota":10000,"transaction-count":259,"endpoint-quota":100,"endpoint-count":1}')
		self._add(	uri="connectorVersion", status=200,
					payload='DeviceServer v3.0.0-520\nREST version = v2')
		self._add(	uri="apiVersion", status=200,
					payload='["v1","v2"]')
		self._add(	uri="endpoints", status=200,
					payload='[{"name":"51f540a2-3113-46e2-aef4-96e94a637b31","type":"test","status":"ACTIVE"}]')
		self._add(	uri="resources", status=200,
					payload='[{"uri":"/Test/0/S","rt":"Static","obs":false,"type":""},{"uri":"/Test/0/D","rt":"Dynamic","obs":true,"type":""},{"uri":"/3/0/2","obs":false,"type":""},{"uri":"/3/0/1","obs":false,"type":""},{"uri":"/3/0/17","obs":false,"type":""},{"uri":"/3/0/0","obs":false,"type":""},{"uri":"/3/0/16","obs":false,"type":""},{"uri":"/3/0/11","obs":false,"type":""},{"uri":"/3/0/11/0","obs":false,"type":""},{"uri":"/3/0/4","obs":false,"type":""}]')
		#self._add(	uri="", status=200,
		#			payload="")
		#self._add(	uri="", status=200,
		#			payload="")
		#self._add(	uri="", status=200,
		#			payload="")

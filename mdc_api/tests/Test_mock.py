# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import mdc_api
import requests
import httpretty
from sure import expect
from nose.tools import *
from mock_data import mockData
import re
import json
from base64 import standard_b64encode as b64encode
import random

# ToDo : change this to make the token pass in through other options
token = "6e4dHnnocri7tJ2zuVmTqLf7CtnSykat9d3x1xd0qZaPp0kV7cALHP25XtvLsMMP2Dp69mDfIJ281ov5iziCaCbRIQvsEelqmxgS"

class asynchMocker:
	"""The asynchMocker class is used to mock asynchronous responses for longpolling """

	_longPollResponseBoilerPlate = {
		"notifications":[
						{
							"ep":"{endpoint-name}",
							"path":"{uri-path}",
							"ct":"{content-type}",
							"payload":"{base64-encoded-payload}",
							"timestamp":"{timestamp}",
							"max-age":"{max-age}"
						}
						],
		"registrations":[
						{
							"ep": "{endpoint-name}",
							"ept": "{endpoint-type}",
							"q": "{queue-mode, default: false}",
							"resources": [ {
								"path": "{uri-path}",
								"if": "{interface-description}",
								"rf": "{resource-type}",
								"ct": "{content-type}",
								"obs": "{is-observable (true|false) }"
							} ]
						}
						],
		"reg-updates":[
						{
							"ep": "{endpoint-name}",
							"ept": "{endpoint-type}",
							"q": "{queue-mode, default: false}",
							"resources": [ {
								"path": "{uri-path}",
								"if": "{interface-description}",
								"rf": "{resource-type}",
								"ct": "{content-type}",
								"obs": "{is-observable (true|false) }"
							} ]
						}
						],
		"de-registrations":[{
							"{endpoint-name}",
							"{endpoint-name2}"
							}],
		"registrations-expired":[{
								"{endpoint-name}",
								"{endpoint-name2}"
								}],
		"async-responses":[{
							"id": "{async-response-id}",
							"status":  "{http-status-code}", #int
							"error":  "{error-message}",		#optional
							"ct":  "{content-type}",
							"max-age": "{max-age}",			#int
							"payload":  "{base64-encoded-payload}"
						}]
	}

	# extend dictionary class so we can instantiate multiple levels at once
	class vividict(dict):
		def __missing__(self, key):
			value = self[key] = type(self)()
			return value

	def generateAsyncID(self):
		return random.randrange(1,9999)

	# used by test infrastructure to directly populate the pending responses
	def add(self, key, value):
		if key == 'async':
			if 'async-responses' not in self._db.keys():
				self._db['async-responses']=[]
			self._db['async-responses'].append(value)
		else:
			print "failed with key : " +key
			assert False # support for this key is not implimented yet

	# entry point for all mocking async api calls
	def input(self,fromWhere):
		if fromWhere == "longPoll" :
			ret = json.dumps(self._db)
			self._db = {}
			return ret
		else:
			asyncID = self.generateAsyncID()
			self.add('async',{
								"id": str(asyncID),
								"status":  200,
								"max-age": 60,
								"payload":  b64encode(str(random.randrange(0,99)))
							})
			return json.dumps({"async-response-id":str(asyncID)})

	def __init__(self):
		self._db = self.vividict() # database to hold async items to be processed
		self._db={}
		return


@httpretty.activate
class test_connector_mock:
	# this function is called before every test function in this class
	# Initialize the mbed connector object and start longpolling
	def setUp(self):
		httpretty.HTTPretty.allow_net_connect = False
		self.connector = mdc_api.connector(token, "http://mock")
		self.connector.apiVersion=""
		#self.connector.debug(True)
		self.md = mockData()
		self.ah = asynchMocker()
		# setup async callback stuffins
		

	# this function is called after every test function in this class
	# stop longpolling
	#def tearDown(self):
		self.connector.stopLongPolling()

	# This function takes an async object and waits untill it is completed
	def waitOnAsync(self,asyncObject):
		while asyncObject.isDone() == False:
			None
		return

	# test the getLimits function GET /limits
	@timed(10)
	def test_getLimits(self):
		httpretty.register_uri(httpretty.GET,re.compile("http://mock/limits"),
								body=self.md.getPayload('limits'),
								status=self.md.getStatusCode('limits'))
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	# test the getConnectorVersion function, GET /
	@timed(10)
	def test_getConnectorVersion(self):
		httpretty.register_uri(httpretty.GET,re.compile("http://mock/"),
								body=self.md.getPayload('connectorVersion'),
								status=self.md.getStatusCode('connectorVersion'))
		x = self.connector.getConnectorVersion()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	# test the getAPIVersion funciton, GET /rest-version
	@timed(10)
	def test_getApiVersion(self):
		httpretty.register_uri(httpretty.GET,re.compile("http://mock/rest-versions"),
								body=self.md.getPayload('apiVersion'),
								status=self.md.getStatusCode('apiVersion'))
		x = self.connector.getApiVersion()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	# test the getEndpoints function, GET /endpoints
	@timed(10)
	def test_getEndpoints(self):
		httpretty.register_uri(httpretty.GET,re.compile("http://mock/endpoints"),
								body=self.md.getPayload('endpoints'),
								status=self.md.getStatusCode('endpoints'))
		x = self.connector.getEndpoints()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	# test the getResources function, GET /endpoints/{endpoint}
	@timed(10)
	def test_getResources(self):
		httpretty.register_uri(httpretty.GET,re.compile("http://mock/endpoints"),
								body=self.md.getPayload('endpoints'),
								status=self.md.getStatusCode('endpoints'))
		httpretty.register_uri(httpretty.GET,re.compile("http://mock/endpoints/(\w\-)+"),
								body=self.md.getPayload('resources'),
								status=self.md.getStatusCode('resources'))
		ep = self.connector.getEndpoints()
		self.waitOnAsync(ep)
		expect(ep.error).to.equal(False)
		x = self.connector.getResources(ep.result[0]['name'])
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	# TODO: this test is not working. currently broken
	@timed(10)
	def test_getResourceValue(self):
		httpretty.register_uri(httpretty.GET,"http://mock/notification/pull",
								body=self.ah.input('longPoll'),
								status=200)
		httpretty.register_uri(httpretty.GET,"http://mock/endpoints",
								body=self.md.getPayload('endpoints'),
								status=self.md.getStatusCode('endpoints'))
		httpretty.register_uri(httpretty.GET,"http://mock/endpoints/51f540a2-3113-46e2-aef4-96e94a637b31", # TODO: replace this with regex
								body=self.md.getPayload('resources'),
								status=self.md.getStatusCode('resources'))
		httpretty.register_uri(httpretty.GET,"http://mock/endpoints/51f540a2-3113-46e2-aef4-96e94a637b31/Test/0/D", # TODO: replace this with regex
								body=self.ah.input('getResourceValue'),
								status=202)
		self.connector.debug(True)
		self.connector.startLongPolling()
		ep = self.connector.getEndpoints()
		self.waitOnAsync(ep)
		expect(ep.error).to.equal(False)
		print "ep.result = "
		print ep.result
		res = self.connector.getResources(ep.result[0]['name'])
		self.waitOnAsync(res)
		expect(res.error).to.equal(False)
		expect(res.isDone()).to.equal(True)
		print "res.result = "
		print res.result
		x = self.connector.getResourceValue("51f540a2-3113-46e2-aef4-96e94a637b31", "/Test/0/D")
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		return

	# TODO: remainder of mocking implementations and impliment the asynch callback mechanism

	#def test_postResource(self):
	#	#TODO
	#	return
	
	#def test_deleteEndpoint(self):
	#	#TODO
	#	return
	
	#def test_putResourceSubscription(self):
	#	#TODO
	#	return
	
	#def test_deleteSubscription(self):
	#	#TODO
	#	return
	
	#def test_deleteEnpointSubscriptions(self):
	#	#TODO
	#	return
	
	#def test_deleteResourceSubscription(self):
	#	#TODO
	#	return
	
	#def test_deleteAllSubscriptions(self):
	#	#TODO
	#	return
	
	#def test_getEndpointSubscriptions(self):
	#	#TODO
	#	return
	
	#def test_getResourceSubscription(self):
	#	#TODO
	#	return
	
	#def test_putPreSubscription(self):
	#	#TODO
	#	return
	
	#def test_getPreSubscription(self):
	#	#TODO
	#	return
	
	#def test_putCallbackURL(self):
	#	#TODO
	#	return
	
	#def test_getCallbackURL(self):
	#	#TODO
	#	return
	
	#def test_deleteCallbackURL(self):
	#	#TODO
	#	return

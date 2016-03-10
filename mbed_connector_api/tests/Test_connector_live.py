# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

# These tests assume a client with the following resources
# endpoint name = 64754207-5e02-4d03-904b-82151ad55ea6
# /ci-object - type:'ci-endpoint'
# 		/static - observable:false, 
#		/dynamic - observable:true, postable:true, this resource will incriment its value every second

import mbed_connector_api
from nose.tools import *
import os

_ep  = '64754207-5e02-4d03-904b-82151ad55ea6'
_objID = 'ci-object'
_resID = 'dynamic'
_res = "/"+_objID+"/0/"+_resID

# Grab the connector token from the 'ACCESS_KEY' environment variable
if 'ACCESS_KEY' in os.environ.keys():
	token = os.environ['ACCESS_KEY'] # get access key from environment variable
else:
	token = "ChangeMe" # replace with your API token


class test_connector_live:
	# this function is called before every test function in this class
	# Initialize the mbed connector object and start longpolling
	def setUp(self):
		self.connector = mbed_connector_api.connector(token)
		self.longPollThread = self.connector.startLongPolling()
		#self.connector.debug(True,level='INFO')

	# this function is called after every test function in this class
	# stop longpolling
	def tearDown(self):
		self.connector.stopLongPolling()

	# This function takes an async object and waits untill it is completed
	def waitOnAsync(self,asyncObject):
		while asyncObject.isDone() == False:
			None
		return

	# test the getLimits function
	@timed(10)
	def test_getLimits(self):
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	# test the getConnectorVersion function	
	@timed(10)
	def test_getConnectorVersion(self):
		x = self.connector.getConnectorVersion()
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	# test the getApiVersion function
	@timed(10)
	def test_getApiVersion(self):
		x = self.connector.getApiVersions()
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	# test the getEndpoints function
	@timed(10)
	def test_getEndpoints(self):
		x = self.connector.getEndpoints()
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	# test the getEndpoints function, subfuntion typeFilter
	@timed(10)
	def test_getEndpointsByType(self):
		x = self.connector.getEndpoints(typeOfEndpoint="ci-endpoint")
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	# test the getResources function
	@timed(10)
	def test_getResources(self):
		x = self.connector.getResources(_ep) # use first endpoint returned
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_getResourceValue(self):
		x = self.connector.getResourceValue(_ep,_res)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_postResource(self):
		# test POST without data
		x = self.connector.postResource(_ep,_res)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))
		# test POST with data
		x = self.connector.postResource(_ep,_res,"Hello World from the CI")
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_deleteEndpoint(self):
		#TODO
		return

	@timed(10)
	def test_putResourceSubscription(self):
		x = self.connector.putResourceSubscription(_ep,_res)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_getEndpointSubscriptions(self):
		x = self.connector.putResourceSubscription(_ep,_res)
		self.waitOnAsync(x)
		assert x.error == False
		x = self.connector.getEndpointSubscriptions(_ep)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_getResourceSubscription(self):
		x = self.connector.putResourceSubscription(_ep,_res)
		self.waitOnAsync(x)
		assert x.error == False
		x = self.connector.getResourceSubscription(_ep,_res)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_deleteResourceSubscription(self):
		# TODO, may need to first subscribe, then unsubscribe?
		x = self.connector.putResourceSubscription(_ep,_res)
		self.waitOnAsync(x)
		assert x.error == False
		x = self.connector.deleteResourceSubscription(_ep,_res)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_deleteEndpointSubscriptions(self):
		x = self.connector.putResourceSubscription(_ep,_res)
		self.waitOnAsync(x)
		assert x.error == False
		x = self.connector.deleteEndpointSubscriptions(_ep)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_deleteAllSubscriptions(self):
		x = self.connector.deleteAllSubscriptions()
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_putPreSubscription(self):
		# check subscription is put-able
		j = [{
				'endpoint-name': "node-001",
				'resource-path': ["/dev"]},
			{
				'endpoint-type': "Light",
				'resource-path': ["/sen/*"]},
			{
				'resource-path': ["/dev/temp","/dev/hum"]
			}]
		x = self.connector.putPreSubscription(j)
		self.waitOnAsync(x)
		ok_(x.error == False, msg=("Error: "+x.error.error+" errType: "+x.error.errType if x.error else ""))

	@timed(10)
	def test_getPreSubscription(self):
		# Check subscription put can be retrieved
		j = [{
				'endpoint-name': "node-001",
				'resource-path': ["/dev"]},
			{
				'endpoint-type': "Light",
				'resource-path': ["/sen/*"]},
			{
				'resource-path': ["/dev/temp","/dev/hum"]
			}]
		e = self.connector.putPreSubscription(j)
		self.waitOnAsync(e)
		ok_(e.error == False, msg="There was an error putting the pre-subscription ")
		e = self.connector.getPreSubscription()
		self.waitOnAsync(e)
		ok_(e.error == False, msg="There was an error getting the pre-subscription ")
		assert e.result == j 

	@timed(10)
	def test_putCallbackURL(self):
		#TODO
		return

	@timed(10)
	def test_getCallbackURL(self):
		#TODO
		return

	@timed(10)
	def test_deleteCallbackURL(self):
		#TODO
		return


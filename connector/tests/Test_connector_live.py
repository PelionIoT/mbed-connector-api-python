# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import api_L1
from nose.tools import *

# ToDo : change this to make the token pass in through other options
token = "CHXKYI7AN334D5WQI9DU9PMMDR8G6VPX3763LOT6"


class test_connector_live:
	# this function is called before every test function in this class
	# Initialize the mbed connector object and start longpolling
	def setUp(self):
		self.connector = api_L1.connector(token)
		self.longPollThread = self.connector.startLongPolling()

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
	@timed(5)
	def test_getLimits(self):
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		assert x.error == False # check for errors

	# test the getConnectorVersion function	
	@timed(5)
	def test_getConnectorVersion(self):
		x = self.connector.getConnectorVersion()
		self.waitOnAsync(x)
		assert x.error == False

	# test the getApiVersion function
	@timed(5)
	def test_getApiVersion(self):
		x = self.connector.getApiVersion()
		self.waitOnAsync(x)
		assert x.error == False

	# test the getEndpoints function
	@timed(10)
	def test_getEndpoints(self):
		x = self.connector.getEndpoints()
		self.waitOnAsync(x)
		assert x.error == False

	# test the getResources function
	@timed(10)
	def test_getResources(self):
		ep = self.connector.getEndpoints() # get list of endpoints
		self.waitOnAsync(ep)
		assert ep.error == False
		if not ep.result:
			ok_(ep.result,msg="There are no endpoints on the domain, thus we cannot get resources. Please make sure to connect a endpoint to the domain that has a readable resource.")
		x = self.connector.getResources(ep.result[0]['name']) # use first endpoint returned
		self.waitOnAsync(x)
		assert x.error == False

	@timed(10)
	def test_getResourceValue(self):
		ep = self.connector.getEndpoints()
		self.waitOnAsync(ep)
		ok_(ep.error == False, msg="There was an error getting the list of endpoints on the domain")
		res = self.connector.getResources(ep.result[0]['name'])
		self.waitOnAsync(res)
		ok_(ep.error == False, msg="There was an error getting the list of resources for the endpoint")
		x = self.connector.getResourceValue(ep.result[0]['name'], res.result[0]['uri'])
		self.waitOnAsync(x)
		assert x.error == False

	@timed(10)
	def test_postResource(self):
		return

	@timed(10)
	def test_deleteEndpoint(self):
		return

	@timed(10)
	def test_putResourceSubscription(self):
		return

	@timed(10)
	def test_deleteSubscription(self):
		return

	@timed(10)
	def test_deleteEnpointSubscriptions(self):
		return

	@timed(10)
	def test_deleteResourceSubscription(self):
		return

	@timed(10)
	def test_deleteAllSubscriptions(self):
		return

	@timed(10)
	def test_getEndpointSubscriptions(self):
		return

	@timed(10)
	def test_getResourceSubscription(self):
		return

	@timed(10)
	def test_putPreSubscription(self):
		return

	@timed(10)
	def test_getPreSubscription(self):
		return

	@timed(10)
	def test_putCallbackURL(self):
		return

	@timed(10)
	def test_getCallbackURL(self):
		return

	@timed(10)
	def test_deleteCallbackURL(self):
		return


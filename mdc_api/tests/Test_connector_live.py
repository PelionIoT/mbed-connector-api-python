# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import mdc_api
from nose.tools import *

# ToDo : change this to make the token pass in through other options
token = "6e4dHnnocri7tJ2zuVmTqLf7CtnSykat9d3x1xd0qZaPp0kV7cALHP25XtvLsMMP2Dp69mDfIJ281ov5iziCaCbRIQvsEelqmxgS"


class test_connector_live:
	# this function is called before every test function in this class
	# Initialize the mbed connector object and start longpolling
	def setUp(self):
		self.connector = mdc_api.connector(token)
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
		assert x.error == False # check for errors

	# test the getConnectorVersion function	
	@timed(10)
	def test_getConnectorVersion(self):
		x = self.connector.getConnectorVersion()
		self.waitOnAsync(x)
		assert x.error == False

	# test the getApiVersion function
	@timed(10)
	def test_getApiVersion(self):
		x = self.connector.getApiVersions()
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
		if not ep.result:
			ok_(ep.result,msg="There are no endpoints on the domain, thus we cannot get resources. Please make sure to connect a endpoint to the domain that has a readable resource.")
		ok_(ep.error == False, msg="There was an error getting the list of endpoints on the domain")
		res = self.connector.getResources(ep.result[0]['name'])
		self.waitOnAsync(res)
		ok_(ep.error == False, msg="There was an error getting the list of resources for the endpoint")
		x = self.connector.getResourceValue(ep.result[0]['name'], res.result[0]['uri'])
		self.waitOnAsync(x)
		assert x.error == False

	@timed(10)
	def test_postResource(self):
		#TODO
		return

	@timed(10)
	def test_deleteEndpoint(self):
		#TODO
		return

	@timed(10)
	def test_putResourceSubscription(self):
		#TODO
		return

	@timed(10)
	def test_deleteSubscription(self):
		#TODO
		return

	@timed(10)
	def test_deleteEnpointSubscriptions(self):
		#TODO
		return

	@timed(10)
	def test_deleteResourceSubscription(self):
		#TODO
		return

	@timed(10)
	def test_deleteAllSubscriptions(self):
		#TODO
		return

	@timed(10)
	def test_getEndpointSubscriptions(self):
		#TODO
		return

	@timed(10)
	def test_getResourceSubscription(self):
		#TODO
		return

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
		e = self.connector.putPreSubscription(j)
		self.waitOnAsync(e)
		assert e.error == False

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


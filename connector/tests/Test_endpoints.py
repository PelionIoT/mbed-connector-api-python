# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import api_L1

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
	def test_getLimits(self):
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		assert x.error == False # check for errors

	# test the getConnectorVersion function	
	def test_getConnectorVersion(self):
		x = self.connector.getConnectorVersion()
		self.waitOnAsync(x)
		assert x.error == False

	# test the getApiVersion function
	def test_getApiVersion(self):
		x = self.connector.getApiVersion()
		self.waitOnAsync(x)
		assert x.error == False

	# test the getEndpoints function
	def test_getEndpoints(self):
		x = self.connector.getEndpoints()
		self.waitOnAsync(x)
		assert x.error == False

	# test the getResources function
	def test_getResources(self):
		ep = self.connector.getEndpoints()
		assert ep.error == False

		x = self.connector.getResources(ep.result[])
		self.waitOnAsync(x)
		assert x.error == False



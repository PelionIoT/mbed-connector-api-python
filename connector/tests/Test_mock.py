# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import api_L1
import requests
import httpretty
from sure import expect
from nose.tools import *
from mock_data import mockData 

# ToDo : change this to make the token pass in through other options
token = "CHXKYI7AN334D5WQI9DU9PMMDR8G6VPX3763LOT6"

@httpretty.activate
class test_connector_mock:
	# this function is called before every test function in this class
	# Initialize the mbed connector object and start longpolling
	def setUp(self):
		self.connector = api_L1.connector(token, "http://mock")
		self.connector.apiVersion=""
		self.md = mockData()
		#self.longPollThread = self.connector.startLongPolling()

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
		httpretty.register_uri(httpretty.GET,"mock://mock/limits",
								body=self.md.getPayload('limits'),
								status=self.md.getStatusCode('limits'))
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	def test_getConnectorVersion(self):
		httpretty.register_uri(httpretty.GET,"mock://mock/limits",
								body=self.md.getPayload('limits'),
								status=self.md.getStatusCode('limits'))
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	def test_getApiVersion(self):
		httpretty.register_uri(httpretty.GET,"mock://mock/",
								body=self.md.getPayload('connectorVersion'),
								status=self.md.getStatusCode('connectorVersion'))
		x = self.connector.getConnectorVersion()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	def test_getEndpoints(self):
		httpretty.register_uri(httpretty.GET,"mock://mock/limits",
								body=self.md.getPayload('limits'),
								status=self.md.getStatusCode('limits'))
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

	def test_getResources(self):
		httpretty.register_uri(httpretty.GET,"mock://mock/limits",
								body=self.md.getPayload('limits'),
								status=self.md.getStatusCode('limits'))
		x = self.connector.getLimits()
		self.waitOnAsync(x)
		expect(x.error).to.equal(False)
		expect(x.isDone()).to.equal(True)
		expect(x.status_code).to.equal(200)

# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.
import requests as r
import json
from base64 import standard_b64decode as b64decode
import threading
import sys
import traceback
from connectorError import response_codes
import logging

class asyncResult:
	"""
	AsyncResult objects returned by all mdc_api library calls. 
	Make sure to check the ``.isDone()`` function and the ``.error`` variable before accessing the ``.result`` variable. 


	:var error: False if no error; if error then populated by :class:'connectorError.response_codes` object.
	:var result: Initial value: {}
	:var status_code: Status code returned from REST request.
	:var raw_data: Raw returned object from the request.
	"""

	def isDone(self):
		""" 
		:returns: True/False based on completion of async operation.
		:rtype: bool.
		"""
		return self.is_done

	def fill(self,  data):
		if type(data) == r.models.Response:
			try:
				self.result =  json.loads(data.content)
			except:
				self.result = []
				if isinstance(data.content,str): # String handler.
					self.result = data.content
				elif isinstance(data.content,int): # Int handler.
					self.log.debug("Data returned is an integer, not sure what to do with that")
				else: # All other handlers.
					self.log.debug("Unhandled data type; type of content: %s" %type(data.content))
			self.status_code = data.status_code
			self.raw_data = data.content
		else:
			#Error
			self.log.error("Type not found : %s"%type(data))
		return

	def __init__(self, callback=""):
		self.is_done = False
		self.result = {}
		self.status_code = ''
		self.raw_data = {}
		self.callback = callback
		self.next_step = ""
		self.extra = {}
		self.error = ""
		self.endpoint = ""
		self.resource = ""

class connector:
	"""
	Interface class to use the connector.mbed.com REST API. 
	This class by default handles asyncronous events.
	All functions return :class:'.asyncResult' objects.
	"""

	# Return Connector version number and recent rest API version numbers it supports.
	def getConnectorVersion(self):
		"""
		GET the current Connector version.

		:returns:  asyncResult object, populates error and result fields.
		:rtype: asyncResult.
		"""
		result = asyncResult()
		data = self._getURL("/",versioned=False)
		result.fill(data)
		if data.status_code == 200:
			result.error = False
		else:
			result.error = response_codes("get_mdc_version",data.status_code)
		result.is_done = True
		return result

	# Return API version of connector.
	def getApiVersions(self):
		"""
		Get the REST API versions that Connector accepts.

		:returns:  :class:asyncResult object, populates error and result fields.
		:rtype: asyncResult.
		"""
		result = asyncResult()
		data = self._getURL("/rest-versions",versioned=False)
		result.fill(data)
		if data.status_code == 200:
			result.error = False
		else:
			result.error = response_codes("get_rest_version",data.status_code)
		result.is_done = True
		return result

	# Return metadata about Connector limits as JSON blob.
	def getLimits(self):
		"""Return limits of account in async result object.

		:returns:  asyncResult object, populates error and result fields.
		:rtype: asyncResult.
		"""
		result = asyncResult()
		data = self._getURL("/limits")
		result.fill(data)
		if data.status_code == 200:
			result.error = False
		else:
			result.error = response_codes("limit",data.status_code)
		result.is_done = True
		return result

	# Return JSON list of all endpoints.
	# Optional type field can be used to match all endpoints of a certain type.
	def getEndpoints(self,typeOfEndpoint=""):
		"""
		Get list of all endpoints on the domain.
		
		:param str typeOfEndpoint: Optional filter endpoints, returned by type.
		:return: List of all endpoints.
		:rtype: asyncResult.
		"""
		q = {}
		result = asyncResult()
		if typeOfEndpoint:
			q['type'] = typeOfEndpoint
			result.extra['type'] = typeOfEndpoint
		data = self._getURL("/endpoints", query = q)
		result.fill(data)
		if data.status_code == 200:
			result.error = False
		else:
			result.error = response_codes("get_endpoints",data.status_code)
		result.is_done = True
		return result

	# Return JSON list of all resources on an endpoint.
	def getResources(self,ep,noResp=False,cacheOnly=False):
		"""
		Get list of resources on an endpoint.
		
		:param str ep: Endpoint to get the resources for.
		:param bool noResp: Optional - specify "no response necessary" from endpoint.
		:param bool cacheOnly: Optional - get results from cache on Connector; do not wake up endpoint.
		:return: List of resources.
		:rtype: asyncResult.
		"""
		# Load query params if set to other than defaults.
		q = {}
		result = asyncResult()
		result.endpoint = ep
		if noResp or cacheOnly:
			q['noResp'] = 'true' if noResp == True else 'false'
			q['cacheOnly'] = 'true' if cacheOnly == True else 'false'
		# Make query
		self.log.debug("ep = %s, query=%s",ep,q)
		data = self._getURL("/endpoints/"+ep, query=q)
		result.fill(data)
		# Check sucess of call.
		if data.status_code == 200: # Sucess
			result.error = False
			self.log.debug("getResources sucess, status_code = `%s`, content = `%s`", str(data.status_code),data.content)
		else: # Fail
			result.error = response_codes("get_resources",data.status_code)
			self.log.debug("getResources failed with error code `%s`" %str(data.status_code))
		result.is_done = True
		return result


	# Return async object.
	def getResourceValue(self,ep,res,cbfn="",noResp=False,cacheOnly=False):
		"""
		Get value of a specific resource on a specific endpoint.
		
		:param str ep: Name of endpoint.
		:param str res: Name of resource.
		:param fnptr cbfn: Optional - callback function to be called on completion.
		:param bool noResp: Optional - specify "no response necessary" from endpoint.
		:param bool cacheOnly: Optional - get results from cache on Connector; do not wake up endpoint.
		:return: Value of the resource, usually a string.
		:rtype: asyncResult.
		"""
		q = {}
		result = asyncResult(callback=cbfn) # Set callback function for use in async handler.
		result.endpoint = ep
		result.resource = res
		if noResp or cacheOnly:
			q['noResp'] = 'true' if noResp == True else 'false'
			q['cacheOnly'] = 'true' if cacheOnly == True else 'false'
		# Make query.
		data = self._getURL("/endpoints/"+ep+res, query=q)
		result.fill(data)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
			if cbfn:
				cbfn(result)
			return result
		elif data.status_code == 202:
			self.database['async-responses'][json.loads(data.content)["async-response-id"]]= result
		else: # Fail
			result.error = response_codes("resource",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# Return async object.
	def putResourceValue(self,ep,res,data,cbfn=""):
		"""
		Put a value to a resource on an endpoint.
		
		:param str ep: Name of endpoint.
		:param str res: Name of resource.
		:param str data: Data to send via PUT.
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		"""
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		result.resource = res
		data = self._putURL("/endpoints/"+ep+res,payload=data)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
		elif data.status_code == 202:
			self.database['async-responses'][json.loads(data.content)["async-response-id"]]= result
		else:
			result.error = response_codes("resource",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# Return async object.
	def postResource(self,ep,res,data="",cbfn=""):
		'''
		POST data to a resource on an endpoint.
		
		:param str ep: Name of endpoint.
		:param str res: Name of resource.
		:param str data: Optional - data to send with POST.
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		result.resource = res
		data = self._postURL("/endpoints/"+ep+res,data)
		if data.status_code == 201: # Immediate success
			result.error = False
			result.is_done = True
		elif data.status_code == 202:
			self.database['async-responses'][json.loads(data.content)["async-response-id"]]= result
		else:
			result.error = response_codes("resource",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# Return async object.
	def deleteEndpoint(self,ep,cbfn=""):
		'''
		Send DELETE message to an endpoint.
		
		:param str ep: Name of endpoint.
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		data = self._deleteURL("/endpoints/"+ep)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
		elif data.status_code == 202:
			self.database['async-responses'][json.loads(data.content)["async-response-id"]]= result
		else:
			result.error = response_codes("resource",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# Subscribe to endpoint or resource. The CBFN is given an asynch object that
	# represents the result. It is up to the user to impliment the notification
	# channel callback in a higher level library.
	def putResourceSubscription(self,ep,res,cbfn=""):
		'''
		Subscribe to changes in a specific resource ``res`` on an endpoint ``ep``
		
		:param str ep: Name of endpoint.
		:param str res: Name of resource.
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		result.resource = res
		data = self._putURL("/subscriptions/"+ep+res)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
		elif data.status_code == 202:
			self.database['async-responses'][json.loads(data.content)["async-response-id"]]= result
		else:
			result.error = response_codes("subscribe",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	def deleteEnpointSubscriptions(self,ep):
		'''
		Delete all subscriptions on specified endpoint ``ep``.
		
		:param str ep: Name of endpoint.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		result.endpoint = ep
		data = self._deleteURL("/subscriptions/"+ep)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
		else:
			result.error = response_codes("delete_endpoint_subscription",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	def deleteResourceSubscription(self,ep,res):
		'''
		Delete subscription to a resource ``res`` on an endpoint ``ep``.
		
		:param str ep: Name of endpoint.
		:param str res: Name of resource.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		result.endpoint = ep
		result.resource = res
		data = self._deleteURL("/subscriptions/"+ep+res)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
		else:
			result.error = response_codes("unsubscribe",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	def deleteAllSubscriptions(self):
		'''
		Delete all subscriptions on the domain (all endpoints, all resources).
		
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		data = self._deleteURL("/subscriptions/")
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
		else:
			result.error = response_codes("unsubscribe",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# Return async object.
	# Result field is a string.
	def getEndpointSubscriptions(self,ep):
		'''
		Get list of all subscriptions on a given endpoint ``ep``.
		
		:param str ep: Name of endpoint.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		result.endpoint = ep
		data = self._getURL("/subscriptions/"+ep)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
			result.result = data.content
		else:
			result.error = response_codes("unsubscribe",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# Return async object.
	# Result field is a string.
	def getResourceSubscription(self,ep,res):
		'''
		Get list of all subscriptions for a resource ``res`` on an endpoint ``ep``.
		
		:param str ep: Name of endpoint.
		:param str res: Name of resource.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		result.endpoint = ep
		result.resource = res
		data = self._getURL("/subscriptions/"+ep+res)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
			result.result = data.content
		else:
			result.error = response_codes("unsubscribe",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	def putPreSubscription(self,JSONdata):
		'''
		Set pre-subscription rules for all endpoints or resources on the domain.
		This can be useful for all current and future endpoints and resources.
		
		:param json JSONdata: Data to use as pre-subscription data. Wildcards are permitted.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		data = self._putURL("/subscriptions",JSONdata, versioned=False)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
			result.result = data.json()
		else:
			result.error = response_codes("presubscription",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	def getPreSubscription(self):
		'''
		Get the current pre-subscription data from Connector.
		
		:return: JSON that represents the pre-subscription data in the ``.result`` field.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		data = self._getURL("/subscriptions")
		if data.status_code == 200: # Immediate success
			result.error = False
			result.is_done = True
			result.result = data.json()
		else:
			result.error = response_codes("presubscription",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	def putCallback(self,url,headers=""):
		'''
		Set the callback URL. To be used in place of long polling when deploying a web app.
		
		**Note**: make sure you set up a callback URL in your web app.
		
		:param str url: Complete URL, including port, where the callback URL is located.
		:param str headers: Optional - headers to have Connector send back with all calls.
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		payloadToSend = {"url":url}
		if headers:
			payload['headers':headers]
		data = self._putURL(url="/notification/callback",payload=payloadToSend, versioned=False)
		if data.status_code == 204: # Immediate success
			result.error = False
			result.result = data.content
		else:
			result.error = response_codes("put_callback_url",data.status_code)
		result.raw_data = data.content
		result.status_code = data.status_code
		result.is_done = True
		return result

	def getCallback(self):
		'''
		Get the callback URL currently registered with Connector. 
		
		:return: Callback URL in ``.result``, error if applicable in ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		data = self._getURL("/notification/callback",versioned=False)
		if data.status_code == 200: # Immediate success
			result.error = False
			result.result = data.json()
		else:
			result.error = response_codes("get_callback_url",data.status_code)
		result.raw_data = data.content
		result.status_code = data.status_code
		result.is_done = True
		return result

	def deleteCallback(self):
		'''
		Delete the Callback URL currently registered with Connector.
		
		:return: Successful ``.status_code`` / ``.is_done``. Check the ``.error``.
		:rtype: asyncResult.
		'''
		result = asyncResult()
		data = self._deleteURL("/notification/callback")
		if data.status_code == 204: # Immediate success
			result.result = data.content
			result.error = False
		else:
			result.error = response_codes("delete_callback_url",data.status_code)
		result.raw_data = data.content
		result.status_code = data.status_code
		result.is_done = True
		return result

	# Set a specific handler to call the CBFN.
	def setHandler(self,handler,cbfn):
		'''
		Register a handler for a particular notification type.
		These are the acceptable notification types: 
		
		| 'async-responses'
		| 'registrations-expired'
		| 'de-registrations'
		| 'reg-updates'
		| 'registrations'
		| 'notifications'

		:param str handler: Name of the notification type.
		:param fnptr cbfn: Function to pass the notification channel messages to.
		:return: Nothing.
		'''
		if handler == "async-responses":
			self.async_responses_callback = cbfn
		if handler == "registrations-expired":
			self.registrations_expired_callback = cbfn
		if handler == "de-registrations":
			self.de_registrations_callback = cbfn
		if handler == "reg-updates":
			self.reg_updates_callback = cbfn
		if handler == "registrations":
			self.registrations_callback = cbfn
		if handler == "notifications":
			self.notifications_callback = cbfn

	# This function needs to spin off a thread that is constantally polling.
	# It should match asynch IDs to values and call their function.
	def startLongPolling(self, noWait=False):
		'''
		Start long polling Connector for notifications.
		
		:param bool noWait: Optional - use the cached values in Connector; do not wait for the device to respond.
		:return: Thread of constantly running long poll. To be used to kill the thred if necessary.
		:rtype: pythonThread.
		'''
		# Check asynch IDs against insternal database of IDs.
		# Call return function with the value given; maybe decode from base64.
		wait = ''
		if(noWait == True):
			wait = "?noWait=true"
		# Check that there isn't another thread already running; only one long polling instance is acceptable.
		if(self.longPollThread.isAlive()):
			self.log.warn("Long polling is already active")
		else:
			# Start infinite long polling thread.
			self._stopLongPolling.clear()
			self.longPollThread.start()
			self.log.info("Spun off long polling thread")
		return self.longPollThread # Return thread instance so user can manually intervene if necessary.

	# Stop long polling by switching the flag off.
	def stopLongPolling(self):
		'''
		Stop long polling thread
		
		:return: none
		'''
		if(self.longPollThread.isAlive()):
			self._stopLongPolling.set()
		else:
			self.log.warn("Long polling thread already stopped")
		return

	# Thread to constantly long poll Connector and process the feedback.
	# TODO: pass wait / noWait on to long polling thread; currently the user can set it but it doesnt actually affect anything.
	def longPoll(self):
		self.log.debug("Long polling started, self.address = %s" %self.address)
		while(not self._stopLongPolling.is_set()):
			try:
				data = r.get(self.address+'/notification/pull',headers={"Authorization":"Bearer "+self.bearer, "Connection":"keep-alive"})
				# Process callbacks.
				if data.status_code != 204: # 204 means no content, do nothing.
					self.handler(data.content)
					self.log.debug("Long poll data = "+data.content)
			except:
				self.log.error("Long polling had an issue and threw an exception")
				ex_type, ex, tb = sys.exc_info()
				traceback.print_tb(tb)
				self.log.error(sys.exc_info())
				del tb
		self.log.info("Killing long polling thread")

	# Parse the notification channel responses and call appropriate handlers.
	def handler(self,data):
		'''
		Function to handle notification data as part of Callback URL handler.
		
		:param str data: Data posted to callback URL by Connector. 
		:return: Nothing.
		'''
		if isinstance(data,r.models.Response):
			self.log.debug("Data is request object =  %s" %str(data.content))
			data = data.content
		elif isinstance(data,str):
			self.log.debug("Data is JSON string = %s" %str(data))
		else:
			self.log.error("Input is not a valid request object or JSON string : %s" %str(data))
			return False
		try:
			data = json.loads(data)
			if 'async-responses' in data.keys():
				self.async_responses_callback(data)
			if 'notifications' in data.keys():
				self.notifications_callback(data)
			if 'registrations' in data.keys():
				self.registrations_callback(data)
			if 'reg-updates' in data.keys():
				self.reg_updates_callback(data)
			if 'de-registrations' in data.keys():
				self.de_registrations_callback(data)
			if 'registrations-expired' in data.keys():
				self.registrations_expired_callback(data)
		except:
			self.log.error("Handle router had an issue and threw an exception")
			ex_type, ex, tb = sys.exc_info()
			traceback.print_tb(tb)
			self.log.error(sys.exc_info())
			del tb

	# Turn debug messages on or off based on the onOff variable.
	def debug(self,onOff):
		'''
		Enable or disable debugging.
		
		:param bool onOff: Turn debugging on or off.
		:return: None.
		'''
		if onOff:
			self.log.setLevel(logging.DEBUG)
			self._ch.setLevel(logging.DEBUG)
		else:
			self.log.setLevel(logging.ERROR)
			self._ch.setLevel(logging.ERROR)

	# Internal async-requests handler.
	# Data input is JSON data.
	def _asyncHandler(self,data):
		try:
			responses = data['async-responses']
			for entry in responses:
				if entry['id'] in self.database['async-responses'].keys():
					result = self.database['async-responses'].pop(entry['id']) # Get the asynch object out of database.
					# Fill in async-result object.
					if 'error' in entry.keys():
						# Error happened; handle it.
						result.error = response_codes('async-responses-handler',entry['status'])
						result.error.error = entry['error']
						result.is_done = True
						if result.callback:
							result.callback(result)
						else: 
							return result
					else:
						# Everything is good, fill it out.
						result.result = b64decode(entry['payload'])
						result.raw_data = entry
						result.status = entry['status']
						result.error = False
						for thing in entry.keys():
							result.extra[thing]=entry[thing]
						result.is_done = True
						# call associated callback function.
						if result.callback:
							result.callback(result)
						else:
							self.log.warn("No callback function given")
				#Else:
					# TODO : object not found in asynch database.
		except:
			# TODO error handling here.
			self.log.error("Bad data encountered and failed to elegantly handle it")
			ex_type, ex, tb = sys.exc_info()
			traceback.print_tb(tb)
			self.log.error(sys.exc_info())
			del tb
			return

	# Default handler for notifications. User should impliment all of these in
	# an L2 implimentation or in their web app.
	# @input Data is a dictionary.
	def _defaultHandler(self,data):
		if 'async-responses' in data.keys():
			self.log.debug("[Default Handler] async-responses detected : ")
			self.log.debug(data["async-responses"])
		if 'notifications' in data.keys():
			self.log.debug("[Default Handler] notifications' detected : ")
			self.log.debug(data["notifications"])
		if 'registrations' in data.keys():
			self.log.debug("[Default Handler] registrations' detected : ")
			self.log.debug(data["registrations"])
		if 'reg-updates' in data.keys():
			# Removed because this happens every 10s or so, spamming the output.
			self.log.debug("[Default Handler] reg-updates detected : ")
			self.log.debug(data["reg-updates"])
		if 'de-registrations' in data.keys():
			self.log.debug("[Default Handler] de-registrations detected : ")
			self.log.debug(data["de-registrations"])
		if 'registrations-expired' in data.keys():
			self.log.debug("[Default Handler] registrations-expired detected : ")
			self.log.debug(data["registrations-expired"])

	# Make the requests.
	# url is the API URL to hit.
	# query are the optional GET params.
	# versioned tells the API whether to hit the /v#/ version. Set to false for
	#  commands that break with this, like the API and Connector version calls.
	# TODO: spin this off to be non-blocking.
	def _getURL(self, url,query={},versioned=True):
		if versioned:
			return r.get(self.address+self.apiVersion+url,headers={"Authorization":"Bearer "+self.bearer},params=query)
		else:
			return r.get(self.address+url,headers={"Authorization":"Bearer "+self.bearer},params=query)

	# Put data to URL with JSON payload in dataIn.
	def _putURL(self, url,payload="",versioned=True):
		if self._isJSON(payload):
			self.log.debug("PUT payload is JSON")
			if versioned:
				return r.put(self.address+self.apiVersion+url,json=payload,headers={"Authorization":"Bearer "+self.bearer})
			else:
				return r.put(self.address+url,json=payload,headers={"Authorization":"Bearer "+self.bearer})
		else:
			self.log.debug("PUT payload is not JSON")
			if versioned:
				return r.put(self.address+self.apiVersion+url,data=payload,headers={"Authorization":"Bearer "+self.bearer})
			else:
				return r.put(self.address+url,data=payload,headers={"Authorization":"Bearer "+self.bearer})

	# Put data to URL with JSON payload in dataIn.
	def _postURL(self, url,payload="",versioned=True):
		if self._isJSON(payload):
			if versioned:
				return r.post(self.address+self.apiVersion+url,json=payload,headers={"Authorization":"Bearer "+self.bearer})
			else:
				return r.post(self.address+url,json=payload,headers={"Authorization":"Bearer "+self.bearer})
		else:
			if versioned:
				return r.post(self.address+self.apiVersion+url,data=payload,headers={"Authorization":"Bearer "+self.bearer})
			else:
				return r.post(self.address+url,data=payload,headers={"Authorization":"Bearer "+self.bearer})

	# Delete endpoint.
	def _deleteURL(self, url,versioned=True):
		if versioned:
			return r.delete(self.address+self.apiVersion+url,headers={"Authorization":"Bearer "+self.bearer})
		else:
			return r.delete(self.address+url,headers={"Authorization":"Bearer "+self.bearer})


	# Check if input is JSON, return true or false accordingly.
	def _isJSON(self,dataIn):
		try:
			json.dumps(dataIn)
			return True
		except:
			self.log.debug("[_isJSON] exception triggered, input is not JSON")
			return False

	# Extend dictionary class so we can instantiate multiple levels at once.
	class vividict(dict):
		def __missing__(self, key):
			value = self[key] = type(self)()
			return value

	# Initialization function, set the token used by this object.
	def __init__(	self,
					token,
					webAddress="https://api.connector.mbed.com",
					port="80",):
		# Set token.
		self.bearer = token
		# Set version of REST API.
		self.apiVersion = "/v2"
		# Init database, used for callback functions for various tasks (asynch, subscriptions, etc).
		self.database = self.vividict()
		self.database['notifications']
		self.database['registrations']
		self.database['reg-updates']
		self.database['de-registrations']
		self.database['registrations-expired']
		self.database['async-responses']
		# Long polling variable.
		self._stopLongPolling = threading.Event() # Must initialize false to avoid race condition.
		self._stopLongPolling.clear()
		# Create thread for long polling.
		self.longPollThread = threading.Thread(target=self.longPoll,name="mdc-api-longpoll")
		self.longPollThread.daemon = True # Do this so the thread exits when the overall process does.
		# Set default webAddress and port to Connector.
		self.address = webAddress
		self.port = port
		# Initialize the callbacks.
		self.async_responses_callback = self._asyncHandler
		self.registrations_expired_callback = self._defaultHandler
		self.de_registrations_callback = self._defaultHandler
		self.reg_updates_callback = self._defaultHandler
		self.registrations_callback = self._defaultHandler
		self.notifications_callback = self._defaultHandler
		# Add logger.
		self.log = logging.getLogger(name="mdc-api-logger")
		self.log.setLevel(logging.ERROR)
		self._ch = logging.StreamHandler()
		self._ch.setLevel(logging.ERROR)
		formatter = logging.Formatter("[%(levelname)s \t %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
		self._ch.setFormatter(formatter)
		self.log.addHandler(self._ch)


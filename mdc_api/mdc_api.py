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


	:var error: False if no error, if error then populated by :class:'connectorError.response_codes` object
	:var result: initial value: {}
	:var status_code: status code returned from REST request
	:var raw_data: raw returned object form the request
	"""

	def isDone(self):
		""" 
		:returns: True / False based on completion of async operation 
		:rtype: bool
		"""
		return self.is_done

	def fill(self,  data):
		if type(data) == r.models.Response:
			try:
				self.result =  json.loads(data.content)
			except:
				self.result = []
				if isinstance(data.content,str): # string handler
					self.result = data.content
				elif isinstance(data.content,int): # int handler
					self.log.debug("data returned is an integer, not sure what to do with that")
				else: # all other handler
					self.log.debug("unhandled data type, type of content : %s" %type(data.content))
			self.status_code = data.status_code
			self.raw_data = data.content
		else:
			#error
			self.log.error("type not found : %s"%type(data))
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
	This class will by default handle asyncronous events.
	All function return :class:'.asyncResult' objects
	"""

	# Return connector version number and recent rest API version number it supports
	def getConnectorVersion(self):
		"""
		GET the current Connector version.

		:returns:  asyncResult object, populates error and result fields
		:rtype: asyncResult
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

	# Return API version of connector
	def getApiVersions(self):
		"""
		Get the REST API versions that connector accepts.

		:returns:  :class:asyncResult object, populates error and result fields
		:rtype: asyncResult
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

	# Returns metadata about connector limits as JSON blob
	def getLimits(self):
		"""return limits of account in async result object.

		:returns:  asyncResult object, populates error and result fields
		:rtype: asyncResult
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

	# return json list of all endpoints.
	# optional type field can be used to match all endpoints of a certain type.
	def getEndpoints(self,typeOfEndpoint=""):
		"""
		Get list of all endpoints on the domain.
		
		:param str typeOfEndpoint: Optional filter endpoints returned by type
		:return: list of all endpoints
		:rtype: asyncResult
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

	# return json list of all resources on an endpoint
	def getResources(self,ep,noResp=False,cacheOnly=False):
		"""
		Get list of resources on an endpoint.
		
		:param str ep: Endpoint to get the resources of
		:param bool noResp: Optional - specify no response necessary from endpoint
		:param bool cacheOnly: Optional - get results from cache on connector, do not wake up endpoint
		:return: list of resources 
		:rtype: asyncResult
		"""
		# load query params if set to other than defaults
		q = {}
		result = asyncResult()
		result.endpoint = ep
		if noResp or cacheOnly:
			q['noResp'] = 'true' if noResp == True else 'false'
			q['cacheOnly'] = 'true' if cacheOnly == True else 'false'
		# make query
		self.log.debug("ep = %s, query=%s",ep,q)
		data = self._getURL("/endpoints/"+ep, query=q)
		result.fill(data)
		# check sucess of call
		if data.status_code == 200: # sucess
			result.error = False
			self.log.debug("getResources sucess, status_code = `%s`, content = `%s`", str(data.status_code),data.content)
		else: # fail
			result.error = response_codes("get_resources",data.status_code)
			self.log.debug("getResources failed with error code `%s`" %str(data.status_code))
		result.is_done = True
		return result


	# return async object
	def getResourceValue(self,ep,res,cbfn="",noResp=False,cacheOnly=False):
		"""
		Get value of a specific resource on a specific endpoint.
		
		:param str ep: name of endpoint
		:param str res: name of resource
		:param fnptr cbfn: Optional - callback function to be called on completion
		:param bool noResp: Optional - specify no response necessary from endpoint
		:param bool cacheOnly: Optional - get results from cache on connector, do not wake up endpoint
		:return: value of the resource, usually a string
		:rtype: asyncResult
		"""
		q = {}
		result = asyncResult(callback=cbfn) #set callback fn for use in async handler
		result.endpoint = ep
		result.resource = res
		if noResp or cacheOnly:
			q['noResp'] = 'true' if noResp == True else 'false'
			q['cacheOnly'] = 'true' if cacheOnly == True else 'false'
		# make query
		data = self._getURL("/endpoints/"+ep+res, query=q)
		result.fill(data)
		if data.status_code == 200: # immediate success
			result.error = False
			result.is_done = True
			if cbfn:
				cbfn(result)
			return result
		elif data.status_code == 202:
			self.database['async-responses'][json.loads(data.content)["async-response-id"]]= result
		else: # fail
			result.error = response_codes("resource",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# return async object
	def putResourceValue(self,ep,res,data,cbfn=""):
		"""
		Put a value to a resource on an endpoint
		
		:param str ep: name of endpoint
		:param str res: name of resource
		:param str data: data to send via PUT
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		"""
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		result.resource = res
		data = self._putURL("/endpoints/"+ep+res,payload=data)
		if data.status_code == 200: #immediate success
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

	#return async object
	def postResource(self,ep,res,data="",cbfn=""):
		'''
		POST data to a resource on an endpoint.
		
		:param str ep: name of endpoint
		:param str res: name of resource
		:param str data: Optional - data to send via POST
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		result.resource = res
		data = self._postURL("/endpoints/"+ep+res,data)
		if data.status_code == 201: #immediate success
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

	# return async object
	def deleteEndpoint(self,ep,cbfn=""):
		'''
		Send DELETE message to an endpoint.
		
		:param str ep: name of endpoint
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		data = self._deleteURL("/endpoints/"+ep)
		if data.status_code == 200: #immediate success
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

	# subscribe to endpoint/resource, the cbfn is given an asynch object that
	# represents the result. it is up to the user to impliment the notification
	# channel callback in a higher level library.
	def putResourceSubscription(self,ep,res,cbfn=""):
		'''
		Subscribe to changes in a specific resource ``res`` on an endpoint ``ep``
		
		:param str ep: name of endpoint
		:param str res: name of resource
		:param fnptr cbfn: Optional - callback funtion to call when operation is completed
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error`` 
		:rtype: asyncResult
		'''
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		result.resource = res
		data = self._putURL("/subscriptions/"+ep+res)
		if data.status_code == 200: #immediate success
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
		Delete all subscriptions on specified endpoint ``ep``
		
		:param str ep: name of endpoint
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error`` 
		:rtype: asyncResult
		'''
		result = asyncResult()
		result.endpoint = ep
		data = self._deleteURL("/subscriptions/"+ep)
		if data.status_code == 200: #immediate success
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
		Delete subscription to a resource ``res`` on an endpoint ``ep``
		
		:param str ep: name of endpoint
		:param str res: name of resource
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult()
		result.endpoint = ep
		result.resource = res
		data = self._deleteURL("/subscriptions/"+ep+res)
		if data.status_code == 200: #immediate success
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
		Delete all subscriptions on the domain (all endpoints, all resources)
		
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult()
		data = self._deleteURL("/subscriptions/")
		if data.status_code == 204: #immediate success
			result.error = False
			result.is_done = True
		else:
			result.error = response_codes("unsubscribe",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# return async object
	# result field is a string
	def getEndpointSubscriptions(self,ep):
		'''
		Get list of all subscriptions on a given endpoint ``ep``
		
		:param str ep: name of endpoint
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult()
		result.endpoint = ep
		data = self._getURL("/subscriptions/"+ep)
		if data.status_code == 200: #immediate success
			result.error = False
			result.is_done = True
			result.result = data.content
		else:
			result.error = response_codes("unsubscribe",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	# return async object
	# result field is a string
	def getResourceSubscription(self,ep,res):
		'''
		Get list of all subscriptions for a resource ``res`` on an endpoint ``ep``
		
		:param str ep: name of endpoint
		:param str res: name of resource
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult()
		result.endpoint = ep
		result.resource = res
		data = self._getURL("/subscriptions/"+ep+res)
		if data.status_code == 200: #immediate success
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
		Set pre-subscription rules for all endpoints / resources on the domain.
		This can be useful for all current and future endpoints/resources.
		
		:param json JSONdata: data to use as pre-subscription data. Wildcards are permitted
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		if isinstance(JSONdata,str) and self._isJSON(JSONdata):
			self.log.warn("pre-subscription data was a string, converting to a list : %s",JSONdata)
			JSONdata = json.loads(JSONdata) # convert json string to list
		if not (isinstance(JSONdata,list) and self._isJSON(JSONdata)):
			self.log.error("pre-subscription data is not valid. Please make sure it is a valid JSON list")
		result = asyncResult()
		data = self._putURL("/subscriptions",JSONdata, versioned=False)
		if data.status_code == 204: # immediate success with no response
			result.error = False
			result.is_done = True
			result.result = []
		else:
			result.error = response_codes("presubscription",data.status_code)
			result.is_done = True
		result.raw_data = data.content
		result.status_code = data.status_code
		return result

	def getPreSubscription(self):
		'''
		Get the current pre-subscription data from connector
		
		:return: JSON that represents the pre-subscription data in the ``.result`` field
		:rtype: asyncResult
		'''
		result = asyncResult()
		data = self._getURL("/subscriptions")
		if data.status_code == 200: #immediate success
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
		Set the callback URL. To be used in place of LongPolling when deploying a webapp.
		
		**note**: make sure you set up a callback URL in your web app
		
		:param str url: complete url, including port, where the callback url is located
		:param str headers: Optional - Headers to have Connector send back with all calls
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult()
		payloadToSend = {"url":url}
		if headers:
			payload['headers':headers]
		data = self._putURL(url="/notification/callback",payload=payloadToSend, versioned=False)
		if data.status_code == 204: #immediate success
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
		
		:return: callback url in ``.result``, error if applicable in ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult()
		data = self._getURL("/notification/callback",versioned=False)
		if data.status_code == 200: #immediate success
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
		
		:return: successful ``.status_code`` / ``.is_done``. Check the ``.error``
		:rtype: asyncResult
		'''
		result = asyncResult()
		data = self._deleteURL("/notification/callback")
		if data.status_code == 204: #immediate success
			result.result = data.content
			result.error = False
		else:
			result.error = response_codes("delete_callback_url",data.status_code)
		result.raw_data = data.content
		result.status_code = data.status_code
		result.is_done = True
		return result

	# set a specific handler to call the cbfn
	def setHandler(self,handler,cbfn):
		'''
		Register a handler for a particular notification type.
		These are the types of notifications that are acceptable. 
		
		| 'async-responses'
		| 'registrations-expired'
		| 'de-registrations'
		| 'reg-updates'
		| 'registrations'
		| 'notifications'

		:param str handler: name of the notification type
		:param fnptr cbfn: function to pass the notification channel messages to.
		:return: Nothing.
		'''
		if handler == "async-responses":
			self.async_responses_callback = cbfn
		elif handler == "registrations-expired":
			self.registrations_expired_callback = cbfn
		elif handler == "de-registrations":
			self.de_registrations_callback = cbfn
		elif handler == "reg-updates":
			self.reg_updates_callback = cbfn
		elif handler == "registrations":
			self.registrations_callback = cbfn
		elif handler == "notifications":
			self.notifications_callback = cbfn
		else:
			self.log.warn("'%s' is not a legitimate notification channel option. Please check your spelling.",handler)

	# this function needs to spin off a thread that is constantally polling,
	# should match asynch ID's to values and call their function
	def startLongPolling(self, noWait=False):
		'''
		Start LongPolling Connector for notifications.
		
		:param bool noWait: Optional - use the cached values in connector, do not wait for the device to respond
		:return: Thread of constantly running LongPoll. To be used to kill the thred if necessary.
		:rtype: pythonThread
		'''
		# check Asynch ID's against insternal database of ID's
		# Call return function with the value given, maybe decode from base64?
		wait = ''
		if(noWait == True):
			wait = "?noWait=true"
		# check that there isn't another thread already running, only one longPolling instance per is acceptable
		if(self.longPollThread.isAlive()):
			self.log.warn("LongPolling is already active.")
		else:
			# start infinite longpolling thread
			self._stopLongPolling.clear()
			self.longPollThread.start()
			self.log.info("Spun off LongPolling thread")
		return self.longPollThread # return thread instance so user can manually intervene if necessary

	# stop longpolling by switching the flag off.
	def stopLongPolling(self):
		'''
		Stop LongPolling thread
		
		:return: none
		'''
		if(self.longPollThread.isAlive()):
			self._stopLongPolling.set()
			self.log.debug("set stop longpolling flag")
		else:
			self.log.warn("LongPolling thread already stopped")
		return

	# Thread to constantly long poll connector and process the feedback.
	# TODO: pass wait / noWait on to long polling thread, currently the user can set it but it doesnt actually affect anything.
	def longPoll(self):
		self.log.debug("LongPolling Started, self.address = %s" %self.address)
		while(not self._stopLongPolling.is_set()):
			try:
				data = r.get(self.address+'/notification/pull',headers={"Authorization":"Bearer "+self.bearer,"Connection":"keep-alive","accept":"application/json"})
				self.log.debug("Longpoll Returned, len = %d, statuscode=%d",len(data.text),data.status_code)
				# process callbacks
				if data.status_code == 200: # 204 means no content, do nothing
					self.handler(data.content)
					self.log.debug("Longpoll data = "+data.content)
			except:
				self.log.error("longPolling had an issue and threw an exception")
				ex_type, ex, tb = sys.exc_info()
				traceback.print_tb(tb)
				self.log.error(sys.exc_info())
				del tb
		self.log.info("Killing Longpolling Thread")

	# parse the notification channel responses and call appropriate handlers
	def handler(self,data):
		'''
		Function to handle notification data as part of Callback URL handler.
		
		:param str data: data posted to Callback URL by connector. 
		:return: nothing
		'''
		if isinstance(data,r.models.Response):
			self.log.debug("data is request object =  %s", str(data.content))
			data = data.content
		elif isinstance(data,str):
			self.log.info("data is json string with len %d",len(data))
			if len(data) == 0:
				self.log.warn("Handler received data of 0 length, exiting handler.")
				return
		else:
			self.log.error("Input is not valid request object or json string : %s" %str(data))
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
			self.log.error("handle router had an issue and threw an exception")
			ex_type, ex, tb = sys.exc_info()
			traceback.print_tb(tb)
			self.log.error(sys.exc_info())
			del tb

	# Turn on / off debug messages based on the onOff variable
	def debug(self,onOff,level='DEBUG'):
		'''
		Enable / Disable debugging 
		
		:param bool onOff: turn debugging on / off
		:return: none
		'''
		if onOff:
			if level == 'DEBUG':
				self.log.setLevel(logging.DEBUG)
				self._ch.setLevel(logging.DEBUG)
				self.log.debug("Debugging level DEBUG enabled")
			elif level == "INFO":
				self.log.setLevel(logging.INFO)
				self._ch.setLevel(logging.INFO)
				self.log.info("Debugging level INFO enabled")
			elif level == "WARN":
				self.log.setLevel(logging.WARN)
				self._ch.setLevel(logging.WARN)
				self.log.warn("Debugging level WARN enabled")
			elif level == "ERROR":
				self.log.setLevel(logging.ERROR)
				self._ch.setLevel(logging.ERROR)
				self.log.error("Debugging level ERROR enabled")
		else:
			self.log.setLevel(logging.ERROR)
			self._ch.setLevel(logging.ERROR)
			self.log.error("Unrecognized debug level `%s`, set to default level `ERROR` instead",level)

	# internal async-requests handler.
	# data input is json data
	def _asyncHandler(self,data):
		try:
			responses = data['async-responses']
			for entry in responses:
				if entry['id'] in self.database['async-responses'].keys():
					result = self.database['async-responses'].pop(entry['id']) # get the asynch object out of database
					# fill in async-result object
					if 'error' in entry.keys():
						# error happened, handle it
						result.error = response_codes('async-responses-handler',entry['status'])
						result.error.error = entry['error']
						result.is_done = True
						if result.callback:
							result.callback(result)
						else: 
							return result
					else:
						# everything is good, fill it out
						result.result = b64decode(entry['payload'])
						result.raw_data = entry
						result.status = entry['status']
						result.error = False
						for thing in entry.keys():
							result.extra[thing]=entry[thing]
						result.is_done = True
						# call associated callback function
						if result.callback:
							result.callback(result)
						else:
							self.log.warn("No callback function given")
				else:
					# TODO : object not found int asynch database
					self.log.warn("No asynch entry for  '%s' found in databse",entry['id'])
		except:
			# TODO error handling here
			self.log.error("Bad data encountered and failed to elegantly handle it. ")
			ex_type, ex, tb = sys.exc_info()
			traceback.print_tb(tb)
			self.log.error(sys.exc_info())
			del tb
			return

	# default handler for notifications. User should impliment all of these in
	# a L2 implimentation or in their webapp.
	# @input data is a dictionary
	def _defaultHandler(self,data):
		if 'async-responses' in data.keys():
			self.log.info("async-responses detected : len = %d",len(data["async-responses"]))
			self.log.debug(data["async-responses"])
		if 'notifications' in data.keys():
			self.log.info("notifications' detected : len = %d",len(data["notifications"]))
			self.log.debug(data["notifications"])
		if 'registrations' in data.keys():
			self.log.info("registrations' detected : len = %d",len(data["registrations"]))
			self.log.debug(data["registrations"])
		if 'reg-updates' in data.keys():
			# removed because this happens every 10s or so, spamming the output
			self.log.info("reg-updates detected : len = %d",len(data["reg-updates"]))
			self.log.debug(data["reg-updates"])
		if 'de-registrations' in data.keys():
			self.log.info("de-registrations detected : len = %d",len(data["de-registrations"]))
			self.log.debug(data["de-registrations"])
		if 'registrations-expired' in data.keys():
			self.log.info("registrations-expired detected : len = %d",len(data["registrations-expired"]))
			self.log.debug(data["registrations-expired"])

	# make the requests.
	# url is the API url to hit
	# query are the optional get params
	# versioned tells the API whether to hit the /v#/ version. set to false for
	#  commands that break with this, like the API and Connector version calls
	# TODO: spin this off to be non-blocking
	def _getURL(self, url,query={},versioned=True):
		if versioned:
			return r.get(self.address+self.apiVersion+url,headers={"Authorization":"Bearer "+self.bearer},params=query)
		else:
			return r.get(self.address+url,headers={"Authorization":"Bearer "+self.bearer},params=query)

	# put data to URL with json payload in dataIn
	def _putURL(self, url,payload="",versioned=True):
		if self._isJSON(payload):
			self.log.debug("PUT payload is json")
			if versioned:
				return r.put(self.address+self.apiVersion+url,json=payload,headers={"Authorization":"Bearer "+self.bearer})
			else:
				return r.put(self.address+url,json=payload,headers={"Authorization":"Bearer "+self.bearer})
		else:
			self.log.debug("PUT payload is NOT json")
			if versioned:
				return r.put(self.address+self.apiVersion+url,data=payload,headers={"Authorization":"Bearer "+self.bearer})
			else:
				return r.put(self.address+url,data=payload,headers={"Authorization":"Bearer "+self.bearer})

	# put data to URL with json payload in dataIn
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

	# delete endpoint
	def _deleteURL(self, url,versioned=True):
		if versioned:
			return r.delete(self.address+self.apiVersion+url,headers={"Authorization":"Bearer "+self.bearer})
		else:
			return r.delete(self.address+url,headers={"Authorization":"Bearer "+self.bearer})


	# check if input is json, return true or false accordingly
	def _isJSON(self,dataIn):
		try:
			json.dumps(dataIn)
			return True
		except:
			self.log.debug("[_isJSON] exception triggered, input is not json")
			return False

	# extend dictionary class so we can instantiate multiple levels at once
	class vividict(dict):
		def __missing__(self, key):
			value = self[key] = type(self)()
			return value

	# Initialization function, set the token used by this object.
	def __init__(	self,
					token,
					webAddress="https://api.connector.mbed.com",
					port="80",):
		# set token
		self.bearer = token
		# set version of REST API
		self.apiVersion = "/v2"
		# Init database, used for callback fn's for various tasks (asynch, subscriptions...etc)
		self.database = self.vividict()
		self.database['notifications']
		self.database['registrations']
		self.database['reg-updates']
		self.database['de-registrations']
		self.database['registrations-expired']
		self.database['async-responses']
		# longpolling variable
		self._stopLongPolling = threading.Event() # must initialize false to avoid race condition
		self._stopLongPolling.clear()
		#create thread for long polling
		self.longPollThread = threading.Thread(target=self.longPoll,name="mdc-api-longpoll")
		self.longPollThread.daemon = True # Do this so the thread exits when the overall process does
		# set default webAddress  and port to mbed connector
		self.address = webAddress
		self.port = port
		# Initialize the callbacks
		self.async_responses_callback = self._asyncHandler
		self.registrations_expired_callback = self._defaultHandler
		self.de_registrations_callback = self._defaultHandler
		self.reg_updates_callback = self._defaultHandler
		self.registrations_callback = self._defaultHandler
		self.notifications_callback = self._defaultHandler
		# add logger
		self.log = logging.getLogger(name="mdc-api-logger")
		self.log.setLevel(logging.ERROR)
		self._ch = logging.StreamHandler()
		self._ch.setLevel(logging.ERROR)
		formatter = logging.Formatter("\r\n[%(levelname)s \t %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
		self._ch.setFormatter(formatter)
		self.log.addHandler(self._ch)


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
	"""For use as part of connector library calls that make asycnronous calls.
		For simple GET calls wait untill the is_done flag is set then read the result and check the status_code.
		For complex calls like Notifications the next_step variable will move the asynch-callback to a notification """

	def isDone(self):
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
	"""Class to create connector objects and manage connections"""

	# Return connector version number and recent rest API version number it supports
	def getConnectorVersion(self):
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
	def getApiVersion(self):
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
		result = asyncResult(callback=cbfn)
		result.endpoint = ep
		result.resource = res
		data = self._putURL("/endpoints/"+ep+res,json=data)
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
		result = asyncResult()
		data = self._deleteURL("/subscriptions/")
		if data.status_code == 200: #immediate success
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
		result = asyncResult()
		data = self._putURL("/subscriptions",JSONdata, versioned=False)
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

	def getPreSubscription(self):
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

	# this function needs to spin off a thread that is constantally polling,
	# should match asynch ID's to values and call their function
	def startLongPolling(self, noWait=False):
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
		if(self.longPollThread.isAlive()):
			self._stopLongPolling.set()
		else:
			self.log.warn("LongPolling thread already stopped")
		return

	# Thread to constantly long poll connector and process the feedback.
	# TODO: pass wait / noWait on to long polling thread, currently the user can set it but it doesnt actually affect anything.
	def longPoll(self):
		self.log.debug("LongPolling Started, self.address = %s" %self.address)
		while(not self._stopLongPolling.is_set()):
			try:
				data = r.get(self.address+'/notification/pull',headers={"Authorization":"Bearer "+self.bearer})
				# process callbacks
				if data.status_code != 204: # 204 means no content, do nothing
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
		if isinstance(data,r.models.Response):
			self.log.debug("data is request object =  %s" %str(data.content))
			data = data.content
		elif isinstance(data,str):
			self.log.debug("data is json string = %s" %str(data))
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
	def debug(self,onOff):
		if onOff:
			self.log.setLevel(logging.DEBUG)
			self._ch.setLevel(logging.DEBUG)
		else:
			self.log.setLevel(logging.ERROR)
			self._ch.setLevel(logging.ERROR)

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
						result.error = connectorError('async-responses-handler',entry['status'])
						result.error.error = entry['error']
						result.is_done = True
						result.callback(result)
					else:
						# everything is good, fill it out
						result.result = b64decode(entry['payload'])
						result.raw_data = payload
						result.status = status_code
						result.error = False
						for thing in entry.keys():
							result.extra[thing]=entry[thing]
						result.is_done = True
						# call associated callback function
						if result.callback:
							result.callback(result)
						else:
							self.log.warn("No callback function given")
				#else:
					# TODO : object not found int asynch database
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
			self.log.debug("[Default Handler] async-responses detected : ")
			self.log.debug(data["async-responses"])
		if 'notifications' in data.keys():
			self.log.debug("[Default Handler] notifications' detected : ")
			self.log.debug(data["notifications"])
		if 'registrations' in data.keys():
			self.log.debug("[Default Handler] registrations' detected : ")
			self.log.debug(data["registrations"])
		#if 'reg-updates' in data.keys():
			# removed because this happens every 10s or so, spamming the output
			#self.log.debug("[Default Handler] reg-updates detected : ")
			#self.log.debug(data["reg-updates"])
		if 'de-registrations' in data.keys():
			self.log.debug("[Default Handler] de-registrations detected : ")
			self.log.debug(data["de-registrations"])
		if 'registrations-expired' in data.keys():
			self.log.debug("[Default Handler] registrations-expired detected : ")
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
		self.longPollThread = threading.Thread(target=self.longPoll,name="mbed-connector-longpoll")
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
		self.log = logging.getLogger(name="mbed-connector-logger")
		self.log.setLevel(logging.ERROR)
		self._ch = logging.StreamHandler()
		self._ch.setLevel(logging.ERROR)
		formatter = logging.Formatter("[%(levelname)s \t %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
		self._ch.setFormatter(formatter)
		self.log.addHandler(self._ch)


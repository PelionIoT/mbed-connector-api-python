# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.
import requests as r
import json
from base64 import standard_b64decode as b64decode
import threading


class connector:
	"""Class to create connector objects and manage connections"""

	def registerCallback(self,url,headers={}):
		#TODO: add support for optional headers, added but not checked to work correctly.
		# TODO: add warning message of len of url + leng of headers > 400 characters
		#TODO : add headers if none given as extra level of security
		data = r.put(self.address+'/notification/callback',json={'url':url,'headers':headers})
		return data.status_code #return status code, no content is returned

	def checkCallback(self,url,headers={}):
		data = r.get(self.address+'/notification/callback',headers={"Authorization":"Bearer "+self.bearer})
		return data.status_code

	def removeCallback(self,url):
		data = r.delete(self.address+'/notification/callback',headers={"Authorization":"Bearer "+self.bearer})
		return data.status_code

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
			print "LongPolling is already active."
		else:
			# start infinite longpolling thread
			self.longPollThread.start()
			print "Spun off LongPolling thread"
		return self.longPollThread # return thread instance so user can manually intervene if necessary

	# Thread to constantly long poll connector and process the feedback.
	# TODO: pass wait / noWait on to long polling thread, currently the user can set it but it doesnt actually affect anything. 
	def longPoll(self,wait = ""):
		while True:
			data = r.get(self.address+'/notification/pull'+wait,headers={"Authorization":"Bearer "+self.bearer})
			self.asyncHandler(data)
			#print("data = "+data.content)

	# Handle callback functions from both long polling and webhooks
	# data is the raw request data returned
	# TODO: handle failed callbacks, ie try to post when posting not allowed
	# TODO: make handler more robust, currently only does stuff for asynch get's, need to handle notifications / subscriptions, errors... etc
	def asyncHandler(self, data):
		#itterate over returned items, if they have a callback fn in ResponseCodeList then call that function, passing in data from asynch callback decoded from base64
		try:
			if 'async-responses' in json.loads(data.content).keys():
				for item in json.loads(data.content)['async-responses'] :
					if item['id'] in self.ResponseCodeList:
						#print("ID : "+self.ResponseCodeList[item['id']]+"\r\nValue :"+b64decode(item['payload'])) #TODO call callback here with passed value
						self.ResponseCodeList[item['id']](b64decode(item['payload'])) #trigger callback function registered with async-response ID and pass it the decoded data value
						return
		except:
			return # value not JSON data, nothing to process here

	def registerPreSubscription(self,preSubscriptionData):
		data = r.put(self.address+'/subscriptions',json=preSubscriptionData)
		return {'data':data.content,'status':data.status_code}

	def subscribeToResource(self,endpoint, resource):
		data = r.put(self.address+"/subscriptions/"+endpoint+"/"+resource,headers={"Authorization":"Bearer "+self.bearer})
		return data.content

	# remove subscription from endpoint/resource, if no params given remove all subscriptions
	def removeSubscription(self,endpoint=None,resource=None):
		if(endpoint == None and resource == None): 
			data = r.delete(self.address+"/subscriptions")
		else:
			data = r.delete(self.address+"/subscriptions/"+endpoint+"/"+resource,headers={"Authorization":"Bearer "+self.bearer})
		return data.content

	# get max number and current used number of packets and endpoints 
	def checkLimit(self):
		data = r.get(self.address+"/limits",headers={"Authorization":"Bearer "+self.bearer})
		return {'data':data.content,'status':data.status_code}

	def getSubscriptions(self):
		data = r.get(self.address+'/subscriptions',headers={"Authorization":"Bearer "+self.bearer})
		return {'data':data.content,'status':data.status_code}

	# return JSON list of endpoints
	# GET /endpoints<?type=typeOfEndpoint>
	def getEndpoints(self, typeOfEndpoint=""):
		if(typeOfEndpoint):
			typeOfEndpoint = "?type="+typeOfEndpoint
		data = r.get(self.address+"/endpoints"+typeOfEndpoint,headers={"Authorization":"Bearer "+self.bearer})
		return {'data':data.content,'status':data.status_code}

	# return JSON list of resources on an endpoint
	def getResources(self,endpoint):
		data = r.get(self.address+"/endpoints/"+endpoint,headers={"Authorization":"Bearer "+self.bearer})
		return {'data':data.content,'status':data.status_code}

	# return value of resource
	def getResource(self,endpoint,resource,callbackFn,cacheOnly=False,noResp=False):
		#TODO: impliment cacheOnly / noResp flags
		options = ""
		if(cacheOnly and noResp):
			options = "?cacheOnly=true&noResp=true"
		elif(cacheOnly):
			options="?cacheOnly=true"
		elif(noResp):
			options="?noResp=true"
		data = r.get(self.address+"/endpoints/"+endpoint+"/"+resource+options,headers={"Authorization":"Bearer "+self.bearer})
		#print('data = '+data.content)
		try:
			if 'async-response-id' in json.loads(data.content).keys():
				self.ResponseCodeList[json.loads(data.content)['async-response-id']] = callbackFn # add callback function for response ID
			#	print("response Code list = "+json.dumps(self.ResponseCodeList))
			return {'data':json.loads(data.content),'status':data.status_code}
		except:
			return False

	# Maybe this should default to put, and have an extra function called Execute resource to post?
	def setResource(self,endpoint,resource,dataIn,cacheOnly=False,noResp=False):
		return

	def putResource(self,endpoint,resource,dataIn):
		data = r.put(self.address+"/endpoints/"+endpoint+"/"+resource,data=dataIn,headers={"Authorization":"Bearer "+self.bearer})
		return {'data':json.loads(data.content),'status':data.status_code}

	def postResource(self,endpoint,resource,dataIn):
		data = r.post(self.address+"/endpoints/"+endpoint+"/"+resource,data=dataIn,headers={"Authorization":"Bearer "+self.bearer})
		return {'data':json.loads(data.content),'status':data.status_code}


	#TODO: write Event handler .on() for registrations, de-registrations, reg-updates, notifications
	#on('registrations', callback)

	# Initialization function, set the token used by this object. 
	def __init__(self,token,webAddress=""):
		# set token
		self.bearer = token
		# Init ResponseCodeList, used for callback fn's for Asynch handling
		self.ResponseCodeList = {}
		#create thread for long polling
		self.longPollThread = threading.Thread(target=self.longPoll,name="mbed-connector-longpoll")
		self.longPollThread.daemon = True # Do this so the thread exits when the overall process does
		# set default webAddress to mbed connector
		if webAddress == '':
			self.address = "https://api.connector.mbed.com"
		else:
			self.address = webAddress

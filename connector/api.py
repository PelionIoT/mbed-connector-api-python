# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.
import requests as r
import json
from base64 import standard_b64decode as b64decode


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

	#this function needs to spin off a thread that is constantally polling, 
	# should match asynch ID's to values and call their function
	# TODO: handle failed callbacks, ie try to post when posting not allowed
	def startLongPolling(self, noWait=False):
		# check Asynch ID's against insternal database of ID's
		# Call return function with the value given, maybe decode from base64?
		wait = ''
		if(noWait == True):
			wait = "?noWait=true"
		#else:
			#TODO: spin this off into a seperate thread that while(1) for duration of class existance
		data = r.get(self.address+'/notification/pull'+wait,headers={"Authorization":"Bearer "+self.bearer})
		#print("data = "+data.content)
		#itterate over returned items, if they have a callback fn in ResponseCodeList then call that function, passing in data from asynch callback decoded from base64
		if 'async-responses' in json.loads(data.content).keys():
			for item in json.loads(data.content)['async-responses'] :
				if item['id'] in self.ResponseCodeList:
					#print("ID : "+self.ResponseCodeList[item['id']]+"\r\nValue :"+b64decode(item['payload'])) #TODO call callback here with passed value
					self.ResponseCodeList[item['id']](b64decode(item['payload'])) #trigger callback function registered with async-response ID and pass it the decoded data value
		return # {'data':json.loads(data.content),'status':data.status_code}

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
	def getEndpoints(self):
		data = r.get(self.address+"/endpoints",headers={"Authorization":"Bearer "+self.bearer})
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
		data = r.get(self.address+"/endpoints/"+endpoint+resource+options,headers={"Authorization":"Bearer "+self.bearer})
		print('data = '+data.content)
		if 'async-response-id' in json.loads(data.content).keys():
			self.ResponseCodeList[json.loads(data.content)['async-response-id']] = callbackFn # add callback function for response ID
		#	print("response Code list = "+json.dumps(self.ResponseCodeList))
		return {'data':json.loads(data.content),'status':data.status_code}

	def setResource(self,endpoint,resource,dataIn,cacheOnly=False,noResp=False):
		options = ""
		if(cacheOnly and noResp):
			options = "?cacheOnly=true&noResp=true"
		elif(cacheOnly):
			options="?cacheOnly=true"
		elif(noResp):
			options="?noResp=true"
		data = r.put(self.address+"/endpoints/"+endpoint+resource+options,data=dataIn,headers={"Authorization":"Bearer "+self.bearer})
		return {'data':data.content,'status':data.status_code}

	def putResource(self,endpoint,resource,dataIn):
		data = r.put(self.address+"/endpoints/"+endpoint+resource,data=dataIn,headers={"Authorization":"Bearer "+self.bearer})
		return {'data':json.loads(data.content),'status':data.status_code}

	def postResource(self,endpoint,resource,dataIn):
		data = r.post(self.address+"/endpoints/"+endpoint+resource,data=dataIn,headers={"Authorization":"Bearer "+self.bearer})
		return {'data':json.loads(data.content),'status':data.status_code}


	#TODO: write Event handler .on() for registrations, de-registrations, reg-updates, notifications
	#on('registrations', callback)

	# Initialization function, set the token used by this object. 
	def __init__(self,token,webAddress=""):
		# set token
		self.bearer = token
		# Init ResponseCodeList, used for callback fn's for Asynch handling
		self.ResponseCodeList = {}
		# set default webAddress to mbed connector
		if webAddress == '':
			self.address = "https://api.connector.mbed.com"
		else:
			self.address = webAddress

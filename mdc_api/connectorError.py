# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

class response_codes:
	"""
	Error class for connector L1 library. Contains the error type, and error string.
	
	:var status_code: status code returned by connector request
	:var errType: combination of parent calling function and status code
	:var error: error given by the https://docs.mbed.com/docs/mbed-device-connector-web-interface docs.
	
	"""
	# list of all possible error tuples
	__errList = {
			# GET Errors
				# GET /
				"get_mdc_version200":"Successful response containing version of mbed Device Connector and recent REST API version it supports.",

				# GET /rest-versions
				"get_rest_version200":"Successful response with a list of version(s) supported by the server.",

				# GET /endpoints
				"get_endpoints200":"Successful response with a list of endpoints.",

				# GET /endpoint/{endpoint-name}
				"get_resources200":"Successful response with a list of metainformation.",
				"get_resources404":"Endpoint not found.",

			# Resource Errors
				#GET, PUT, POST, DELETE /endpoints/{endpoint-name}/{resource-path}
				"resource200":"Successful GET, PUT, DELETE operation.",
				"resource201":"Successful POST operation.",
				"resource202":"Accepted. Asynchronous response ID.",
				"resource204":"Non confirmable request made, this may or may not reach the endpoint. No Content given as response.",
				"resource205":"No cache available for resource.",
				"resource404":"Requested endpoint's resource is not found.",
				"resource409":"Conflict. Endpoint is in queue mode and synchronous request can not be made. If noResp=true, the request is not supported.",
				"resource410":"Gone. Endpoint not found.",
				"resource412":"Request payload has been incomplete.",
				"resource413":"Precondition failed.",
				"resource415":"Media type is not supported by the endpoint.",
				"resource429":"Cannot make a request at the moment, already ongoing other request for this endpoint or queue is full (for endpoints in queue mode).",
				"resource502":"TCP or TLS connection to endpoint is not established.",
				"resource503":"Operation cannot be executed because endpoint is currently unavailable.",
				"resource504":"Operation cannot be executed due to a time-out from the endpoint.",

			# Subscription / Notification Errors
				# PUT /subscriptions/{endpoint-name}/{resource-path}
				"subscribe200":"Successfully subscribed.",
				"subscribe202":"Accepted. Asynchronous response ID.",
				"subscribe404":"Endpoint or its resource not found.",
				"subscribe412":"Cannot make a subscription for a non-observable resource.",
				"subscribe413":"Cannot make a subscription due to failed precondition.",
				"subscribe415":"Media type is not supported by the endpoint.",
				"subscribe429":"Cannot make subscription request at the moment due to already ongoing other request for this endpoint or (for endpoints in queue mode) queue is full or queue was cleared because endpoint made full registration.",
				"subscribe502":"Subscription failed.",
				"subscribe503":"Subscription could not be established because endpoint is currently unavailable.",
				"subscribe504":"Subscription could not be established due to a time-out from the endpoint.",

				# DELETE /subscriptions/{endpoint-name}/{resource-path}
				# DELETE /subscriptions
				"unsubscribe204":"Successfully removed subscription.",
				"unsubscribe404":"Endpoint or endpoint's resource not found.",

				# GET /subscriptions/{endpoint-name}/{resource-path}
				"get_resource_subscription200":"Resource is subscribed.",
				"get_resource_subscription404":"Resource is not subscribed.",

				# GET /subscriptions/{endpoint-name}
				"get_endpoint_subscription200":"List of subscribed resources.",
				"get_endpoint_subscription404":"Endpoint not found or there are no subscriptions for that endpoint.",

				# DELETE /subscriptions/{endpoint-name}
				"delete_endpoint_subscription204":"Successfully removed.",
				"delete_endpoint_subscription404":"Endpoint not found.",

				# GET /subscriptions - Presubscription Data
				# Nothing yet?
				"put_callback_url204":"Successfully set pre-subscription data.",
				"put_callback_url400":"Malformed content.",

			# Callback
				# PUT /notification/callback
				"put_callback_url204":"Successfully subscribed.",
				"put_callback_url400":"Given URL is not accessible.",

				# GET /notification/callback
				"get_callback_url200":"URL found.",
				"get_callback_url404":"Callback URL does not exist.",

				# DELETE /notification/callback
				"delete_callback_url204":"Successfully removed.",
				"delete_callback_url404":"Callback URL does not exist.",

			# Long polling
				# GET /notification/pull
				"longpoll200":"OK.",
				"longpoll204":"No new notifications.",

			# Limits
				# GET /limits
				"limit200":"OK.",
	}

	# set the error type by querying the __errList
	def _setError(self,errType):
		if errType in self.__errList.keys():
			return self.__errList[errType]
		else:
			return "ERROR: Unknown error."

	def __init__(self,errParent,status_code):
		self.status_code = status_code
		self.errType = str(errParent)+str(status_code)
		self.error = self._setError(self.errType)

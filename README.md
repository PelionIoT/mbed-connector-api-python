## mbed-connector-python 
A python package to use the [mbed Device Connector](connector.mbed.com) REST interface to control IoT devices running [mbed Client](https://www.mbed.com/en/development/software/mbed-client/)
[![Build Status](https://travis-ci.com/ARMmbed/mbed-connector-python.svg?token=Dx5hVfbwqW4x3Gceyoaw&branch=master)](https://travis-ci.com/ARMmbed/mbed-connector-python)
[![Circle CI](https://circleci.com/gh/ARMmbed/mbed-connector-python.svg?style=svg&circle-token=31558742681378e1069cf4e06fc0c317dfa72eb0)](https://circleci.com/gh/ARMmbed/mbed-connector-python)

### Purpose
This library is meant to be used in conjuntion with the [connector.mbed.com](www.connector.mbed.com) service. This library uses the requests library to interface to mbed connector via HTTP REST calls. Details on the mbed connector RESTful interface can be found [here](https://docs.mbed.com/docs/mbed-client-guide/en/latest/Introduction/#how-to-use-the-api). You can use this library either as part of a webapp or locally on your computer.

### API
see docs folder or TODO: hosted instance of docs

### Installation

#### pip
Install the mdc-api package from pip. You may need to use `sudo` on your system. 
```python
pip install -U mdc_api
```

#### setup.py
Clone the repository, then run the following command inside the downloaded folder. 

```python
sudo python setup.py install
```

### Examples
These examples demonstrate how to use the mbed-connector python library in two instances. The first example is a remotely hosted webapp where a public URL can be registered as a webhook callback address. Second is locally on your computer where you will use LongPolling to constantly poll the server for responses to your requests. LongPolling is necessary as machines behind firewalls cannot easily register a public url to handle callbacks / webhooks.  
There are more examples in the Docs.

##### web app
For a web app we do not need long polling, instead we can simply register a webhook url and then handle all callbacks to that URL appropriately. This method is reccomended for releases as it is less resource intensive than constantly long polling. 
```python
import web
import mdc_api
import json

# map URL to class to handle requests
urls = (
	'/', 'index',
	'/callbackURL','callbackFunction',
	'/start','start',
)

token = "CHANGEME" # Get from connector.mbed.com
connector = mdc_api.connector(token)

class index:
	def GET(self):
		return "Hi there, please click 'start' to begin polling mbed Device Connector"

class callbackFunction:
	# handle asynchronous events
	def PUT(self):
		if web.data: # verify there is data to process
			print json.loads(web.data()).keys()
			connector.handler(web.data()) # hand the data to the connector handler
		return web.ok

# 'notifications' are routed here
def notificationHandler(data):
	print "\r\nNotification Data Received :\r\n %s" %data['notifications']


class start:
	def GET(self):
		e = connector.putCallback("https://python-workspace-mbedaustin.c9users.io:8080/callbackURL")
		while not e.isDone():
			None
		if e.error:
			return e.error.errType
		else:
			connector.setHandler('notifications', notificationHandler) # send 'notifications' to the notificationHandler FN
			return "Roger Dodger, started her up!"
			
if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()
	connector.debug(True) # turn on optional debugging
	e = connector.putCallback("https://python-workspace-mbedaustin.c9users.io:8080/callbackURL") # Change to match your workspace
	while not e.isDone():
		None
	if e.error:
		print "ERROR in initialization : " + e.error.errType
```
In the code above you can see the webhook URL accepts PUT requests. In the initialization of the flask webapp we register the callback to connector with `putCallback("mywebapp.com:8080/webhook)`. You will need to change `mywebapp.com` to match the public url of your web app, also change the `8080` to the port your web app is running on.


##### locally hosted
Using the library locally on your computer will require the use of LongPolling. To initialize the library you will need to import it and then instantiate an instance with the API key taken from [connector.mbed.com](https://connector.mbed.com/#accesskeys). Next you will need to `startLongPolling()` which will spin off a thread that will constantly ping the mbed connector service, when it finds updates that match requests you have made it will trigger the callback function you registered. 

```python
# Initialization
import mdc_api
x = mdc_api.connector("insert api key from [connector.mbed.com](https://connector.mbed.com/#accesskeys)")
x.startLongPolling()

# Use 
x.getEndpoints() # returns a  list of all endpoints on your domain
x.getResources("EndpointName") # returns all resources of an endpoint
x.putResourceValue("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a PUT request
x.postResourceValue("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a POST request
y = x.getResourceValue("EndpointName","Resource")  # check the y.isDone() funciton to see when the request completes, the result will then be in y.result. The Resource should be of the form "/X/Y/Z"
if y.isDone():
    if not y.error:
        print("The value of y is " +y.result)
    else:
        print("Error : %s",y.error.error)

##########

# alternatively you can call a callback fn instead
def callbackFn(dataIn, rawData):
    print "TestFN"
    print "data : " +str(dataIn)
    print "raw JSON Data : " +str(rawData)

x.getResourceValue("EndpointName","Resource",callbackFn)

##########

x.subscribeToResource("Endpoint","Resource",callbackFN) # This will call the callbackFn every time the Endpoint/Resource value changes.

```

### Extras
#### Debug
This module uses the logging module. To enable more robust debugging initialize your object instance and then use the `.debug(True)` method to enable more robust debugging of the module

### Requirements
This module uses the `requests` library. If you do not have it installed please install it. 

### License
Apache 2.0
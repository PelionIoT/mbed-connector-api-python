## Purpose
This library is meant to be used in conjuntion with the [connector.mbed.com](www.connector.mbed.com) service. This library uses the requests library to interface to mbed connector via HTTP REST calls. Details on the mbed connector RESTful interface can be found [here](https://docs.mbed.com/docs/mbed-client-guide/en/latest/Introduction/#how-to-use-the-api). You can use this library either as part of a webapp or locally on your computer.

## API
see docs folder or TODO: hosted instance of docs

## Installation
Clone the repository, then run the following command inside the downloaded folder. 

```python
sudo python setup.py install
```

## Examples
These examples demonstrate how to use the mbed-connector python library in two instances. The first example is a remotely hosted webapp where a public URL can be registered as a webhook callback address. Second is locally on your computer where you will use LongPolling to constantly poll the server for responses to your requests. LongPolling is necessary as machines behind firewalls cannot easily register a public url to handle callbacks / webhooks.  
There are more examples in the Docs.

#### web app
For a web app we do not need long polling, instead we can simply register a webhook url and then handle all callbacks to that URL appropriately. This method is reccomended for releases as it is less resource intensive than constantly long polling. 
```python
import mdc_api
from flask import Flask, request
app = Flask(__name__)

token = "CHXKYI7AN334D5WQI9DU9PMMDR8G6VPX3763LOT6"
connector = mdc_api.connector(token)

@app.route("/webhook", methods=['PUT', 'GET'])
def webhook():
    if request.method == 'PUT':
        data = request.data
        print 'webhook triggered with data: `%s`'%data
        return 'OK'

def notificationHandler(notification):
    print "Notification Received : "+str(notification)

if __name__ == '__main__':
    connector.putCallback("http://mywebapp.com:8080/webhook")
    connector.setHandler('notifications', notificationHandler)
    app.run()
```
In the code above you can see the webhook URL accepts PUT requests. In the initialization of the flask webapp we register the callback to connector with `putCallback("mywebapp.com:8080/webhook)`. You will need to change `mywebapp.com` to match the public url of your web app, also change the `8080` to the port your web app is running on.


#### locally hosted
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
    print "The value of y is " +str(y.result)

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

## Extras
#### Debug
This module uses the logging module. To enable more robust debugging initialize your object instance and then use the `.debug(True)` method to enable more robust debugging of the module

## Requirements
This module uses the `requests` library. If you do not have it installed please install it. 

## License
Apache 2.0
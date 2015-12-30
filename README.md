## Intro
This library is meant to be used in conjuntion with [connector.mbed.com](www.connector.mbed.com). This library uses the requests library to interface over HTTP REST calls with mbed connector. Details on the rest interface can be found [here](https://docs.mbed.com/docs/mbed-client-guide/en/latest/Introduction/#how-to-use-the-api). You can use this library either as part of a webapp or on your computer. 

## Examples
These examples demonstrate how to use the mbed-connector python library in two instances. First is remotely on as part of a webapp where you will register a callback address. Second is locally on your computer where you will use LongPolling to constantly poll the server for responses to your requests. This is necessary as machines behind firewalls cannot easily register url callbacks.  
#### web app
TODO: put in Flask webapp example
#### local on computer

```python
import mbed-connector
x = api(<insert api key from [connector.mbed.com#console](https://connector.mbed.com/#accesskeys)>)
x.startLongPolling() 
x.getEndpoints() # this will list out all endpoints on your domain
x.getResources("EndpointName") # this will get all the resources of an endpoint
x.getResource("EndpointName","Resource", callbackFN) # This will pass the resource value to the callbackFN, the <resource> will have the form of "X/Y/Z" 
x.putResource("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a PUT request
x.postResource("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a POST request

# TODO: Subscriptions / Notifications
```

## Liscense
Apache 2.0
## Warning
This is still in internal Alpha and should not be released to the public or to partners. This is a proof of concept to spur the creation of a more general library and a better API. The goal is to eventually have a meta language to write the interface API in that generates code for python, ruby, nodeJS and others. 

## Purpose
This library is meant to be used in conjuntion with the [connector.mbed.com](www.connector.mbed.com) service. This library uses the requests library to interface to mbed connector via HTTP REST calls. Details on the mbed connector RESTful interface can be found [here](https://docs.mbed.com/docs/mbed-client-guide/en/latest/Introduction/#how-to-use-the-api). You can use this library either as part of a webapp or locally on your computer.

## API
TODO

## Examples
These examples demonstrate how to use the mbed-connector python library in two instances. The first example is a remotely hosted webapp where a public URL can be registered as a webhook callback address. Second is locally on your computer where you will use LongPolling to constantly poll the server for responses to your requests. LongPolling is necessary as machines behind firewalls cannot easily register a public url to handle callbacks / webhooks.  
#### web app
For a web app we do not need long polling, instead we can simply register a webhook url and then handle all callbacks to that URL appropriately. This method is reccomended for releases as it is less resource intensive than constantly long polling. 
```python
TODO: put in Flask webapp example
```

#### locally hosted
Using the library locally on your computer will require the use of LongPolling. To initialize the library you will need to import it and then instantiate an instance with the API key taken from [connector.mbed.com](https://connector.mbed.com/#accesskeys). Next you will need to `startLongPolling()` which will spin off a thread that will constantly ping the mbed connector service, when it finds updates that match requests you have made it will trigger the callback function you registered. 

```python
# Initialization
import mbed-connector
x = api("insert api key from [connector.mbed.com](https://connector.mbed.com/#accesskeys)")
x.startLongPolling()

# Use 
x.getEndpoints() # returns a  list of all endpoints on your domain
x.getResources("EndpointName") # returns all resources of an endpoint
x.putResource("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a PUT request
x.postResource("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a POST request
y = x.getResource("EndpointName","Resource")  # check the y.isDone() funciton to see when the request completes, the result will then be in y.result. The Resource should be of the form "/X/Y/Z"
if y.isDone():
    print "The value of y is " +str(y.result)

##########

# alternatively you can call a callback fn instead
def callbackFn(dataIn, rawData):
    print "TestFN"
    print "data : " +str(dataIn)
    print "raw JSON Data : " +str(rawData)

x.getResource("EndpointName","Resource",callbackFn)

##########

x.subscribeToResource("Endpoint","Resource",callbackFN) # This will call the callbackFn every time the Endpoint/Resource value changes.

```

## License
Apache 2.0
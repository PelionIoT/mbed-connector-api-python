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
x.getResource("EndpointName","Resource", callbackFN) # This will pass the resource value to the callbackFN, the <resource> will have the form of "X/Y/Z" 
x.putResource("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a PUT request
x.postResource("EndpointName","Resource","Value") # send the "Value" to the "Resource" over a POST request

# TODO: Subscriptions / Notifications
```

## License
Apache 2.0
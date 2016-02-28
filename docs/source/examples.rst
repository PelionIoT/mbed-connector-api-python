Examples
========

How to use async objects
-------------------------
asyncResult objects have several useful fields. After each API call you should do the following:
    1. Check the ``.isDone()`` function. This returns ``True`` when the operation has completed.
    2. Check the ``.error`` variable. If it is set to ``False`` then there is no error. If it is not ``False`` then the ``.error`` variable contains a ``connectorError`` object.
    3. Read the ``.result`` variable to get the result of the API action. 

.. code-block:: python

    # x is an initialized Connector object
    e = x.getEndpoints()
    while not e.isDone():
        None
    if e.error:
        print("Error : %s",e.error.error)
    else:
        print("Result is %s",e.result)
    
How to use connectorError objects
----------------------------------
You will probably only encounter this object when something has gone wrong. To find what the error was you can check the ``.error`` variable, which contains a string representing the error. The ``.status_code`` variable contains the returned status code related to the error. 

.. code-block:: python

    # x is an initialized mbed_connector_api object
    e = x.getEndpoints()
    if e.error:
        print e.error.error         # Error message
        print e.error.errType       # Error type
        print e.error.status_code   # Error status code



Long polling 
-------------
When running code on your local machine you will want to use long polling instead of a callback URL (webhook). This is because your local machine does not have a publically addressable IP, so it cannot register a webhook. You should start longpolling before doing any other operations as the long poll will serve as a notification channel between Connector and your app. 

.. code-block:: python

    import mbed_connector_api                       # Import library
    x = mbed_connector_api.connector("API-Token")   # Initialize object
    x.startLongPolling()                            # Start long polling
    # ... Do stuff


Callback URL (webhook)
-----------------------
Instead of long polling you can use a callback URL, also known as a webhook. To do this you will need a public web address for your web app and a function that can receive PUT requests. You can use the ``.putCallback('url')`` function to register the callback URL with Connector. It is important that the callback URL be publically accessible, otherwise the registration will fail. The code below assums you are using the ``web.py`` library. 

.. code-block:: python

    import web
    import mbed_connector_api
    import json
    
    # map URL to class to handle requests
    urls = (
    	'/', 'index',
    	'/callback','callbackHandler',
    )
    
    token = "Change Me" # Put your api token here
    connector = mbed_connector_api.connector(token)

    class index:
	    def GET(self):
		    return "Hi there, please click 'start' to begin polling mbed Device Connector"
	
	# This function is where the callbackURL will route to
	class callbackHandler:
	    # handle asynchronous events from connector
    	def PUT(self):
    		if web.data: # verify there is data to process
    			print json.loads(web.data()).keys() # print the notification types being passed by connector
    			connector.handler(web.data()) # hand the data to the connector handler
    		return web.ok
    	
	def registerCallbackURL():
        e = connector.putCallback('https://myHostName/callback') # change myHostName to match the host name of the server where webapp is hosted.
        while not e.isDone():
            None
        if e.error:
            raise Exception(p.error.errType)
        else:
            print("Sucessfully registed callback URL!")
    
    if __name__ == "__main__":
    # 2s after webpy starts we register notification
    t = Timer(2, registerCallbackURL)
    t.start()

    app = web.application(urls, globals())
    app.run()


List all endpoints
-------------------
Get all endpoints by using the ``getEndpoints()`` function.

.. code-block:: python

    # x is an initialized mbed_connector_api object
    r = x.getEndpoints()
    while not r.isDone():   # Wait for asynch operation to complete
        None
    if r.error:     # Check whether there was an error
        print("Error : %s",r.error.error)
    else:
        print r.result  # No error; grab the list of endpoints

    Example Output:
    >>> [{u'name': u'0388e9a4-274e-4709-b568-384198942573', u'status': u'ACTIVE', u'type': u'linux-test'}]

List endpoint resources
------------------------
Get all resources on an endpoint by using the ``getResources()`` function. 

.. code-block:: python

    # x is an initialized mbed_connector_api object
    r = x.getResources("endpointName")
    while not r.isDone():
        None
    if r.error:
        print("Error : %s",r.error.error)
    else:
        print r.result
    
    Example Output
    >>> [{u'obs': False, u'rt': u'ResourceTest', u'type': u'', u'uri': u'/Test/0/S'},
        {u'obs': True, u'rt': u'ResourceTest', u'type': u'', u'uri': u'/Test/0/D'},
        {u'obs': False, u'type': u'', u'uri': u'/3/0'}]


GET resource value
-------------------
Get the value of a resource on an endpoint.

.. code-block:: python

    # Callback function to handle result and pass asyncResult object
    def test(data):
        if data.error:
            print("Error: %s", data.error.error)
        else:
            print("Resource Value = %s",data.result)

    # x is an initialized mbed_connector_api object
    r = x.getResourceValue(ep="EndpointName",res="ResourceName",cbfn=test)


PUT value to resource
----------------------
Change the value of a resource on an endpoint by using ``PUT``.

.. code-block:: python

    # x is an initialized mbed_connector_api object
    r = x.putResourceValue('EndpointName','ResourceName','DataToSend')

    
POST value to resource
-----------------------
POSTing a value to a resource triggers the associated callback function and passes optional data to it. This method is usually used to trigger events.

.. code-block:: python

    # x is an initialized mbed_connector_api object
    r = x.postResource('EndpointName','ResourceName','Optional Data')


Subscribe to resource
----------------------
Subscribe to a resource to automatically be notified of changes to resource values. Note that all changes to the resource value are received in the notification channel (long polling or callback URL (webhook).

.. code-block:: python 

    # x is an initialized mbed_connector_api object
    r = x.pubResourceSubscription('endpointName','resourceName')



DELETE subscriptions
---------------------
You can delete subscriptions at three levels.

    1. Delete single resource subscription: ``deleteResourceSubscription('endpoint','resource')``.
    2. Delete all subscriptions on an endpoint: ``deleteEnpointSubscriptions('endpoint')``.
    3. Delete all resource subscriptions on all endpoints on domain: ``deleteAllSubscriptions()``.


Pre-subscription
-----------------
You can use pre-subscriptions to subscribe to all domain resources or endpoints that match a certain pattern. This applies to both existing and future resources.

.. code-block:: python
   
    #TODO < CODE HERE>
    

Enable debug
-------------
If you want debug messages to be printed to the terminal, you need to enable debug for your mbed_connector_api object. By default, debugging displays all notification channel messages.

.. code-block:: python

    # Enable Debug
    x.debug(True) # Turn on debug
    
    # Set debug message levels
    # 'ERROR','WARN','INFO','DEBUG' levels can be optionally provided
    x.debug(True,'INFO')    # display messages >= INFO
    x.debug(True,'DEBUG')   # display messages >= DEBUG
    
    # Turn Debugging off
    x.debug(False)

Add notification channel handler
---------------------------------
Add a function to handle different message types on the notification channel.
The following notifications types are permitted:
    
    1. ``‘async-responses’``: handled by api_L1, can be overridden.
    2. ``‘registrations-expired’``: endpoint has disappeared.
    3. ``‘de-registrations’``: endpoint has willingly left.
    4. ``‘reg-updates’``: endpoint has pinged Connector.
    5. ``‘registrations’``: new endpoints added to domain.
    6. ``‘notifications’``: subscribed resource value changed.
    
For more information see the [Connector docs](https://docs.mbed.com/docs/mbed-device-connector-web-interfaces).

.. code-block:: python

    
    def test(message):
        print("Received Notification message : %s", message)

    # x is an initialized mbed_connector_api object
    x.sethandler('notifications', test)


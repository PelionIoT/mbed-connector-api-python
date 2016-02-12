Examples
========

How to use Async Objects
--------------------------
AsyncResult objects have several useful fields. After each api call you should do the following:
    1. Check the ``.isDone()`` function. This will return True when the operation has completed.
    2. Check the ``.error`` variable. If it is set to ``False`` then there is no error. If it is not ``False`` then the ``.error`` variable contains a ``connectorError`` object.
    3. Read the ``.result`` variable to get the result of the API action. 

.. code-block:: python

    # x is initialized connector object
    e = x.getEndpoints()
    while not e.isDone():
        None
    if e.error:
        print("Error : %s",e.error.error)
    else:
        print("Result is %s",e.result)
    
How to use ConnectorError Objects
----------------------------------
Connector Error objects contain several fields. In general you will probably one encounter this object when something has gone wrong. To find what the error was you can check the ``.error`` variable which will contain a string representing the error. The ``.status_code`` variable contains the returned status code related to the error. 

.. code-block:: python

    # x is initialized api_L1 object
    e = x.getEndpoints()
    if e.error:
        print e.error.error         # Error message
        print e.error.errType       # Error Type
        print e.error.status_code   # Error status code



Long Polling 
-------------
When running code on your local machine you will want to use LongPolling instead of a callback URL / webhook. You must set up a notification channel before any other operations can be used. 

.. code-block:: python

    import connector.api_L1 # import library
    x = api_L1("API-Token") # initialize object
    x.startLongPolling()    # start long polling
    # ... Do stuff


Callback URL / Webhook
-----------------------
TODO <INSERT HERE>

List all Endpoints
-------------------
Get all endpoints by using the ``getEndpoints()`` function.

.. code-block:: python

    # x is initialized api_L1 object
    r = x.getEndpoints()
    while not r.isDone():   # wait for asynch operation to complete
        None
    if r.error:     # check if there was an error
        print("Error : %s",r.error.error)
    else:
        print r.result  # no error, grab the list of endpoints!

    Example Output:
    >>> []

List Resources on Endpoint
---------------------------
Get all resources on an endpoint by using the ``getResources()`` function. 

.. code-block:: python

    # x is initialized api_L1 object
    r = x.getResources("endpointName")
    while not r.isDone():
        None
    if r.error:
        print("Error : %s",r.error.error)
    else:
        print r.result
    
    Example Output
    >>> []


Get value of resource 
----------------------
Get the value of a resource on an Endpoint.

.. code-block:: python

    # callback function to handle result, pass asyncResult object
    def test(data):
        if data.error:
            print("Error: %s", data.error.error)
        else:
            print("Resource Value = %s",data.result)

    # x is initialized api_L1 object
    r = x.getResourceValue(ep="EndpointName",res="ResourceName",cbfn=test)
    
    

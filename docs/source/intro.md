=====
Intro
=====

The mbed-connector-python module is an interface to the `connector.mbed.com REST API <https://docs.mbed.com/docs/mbed-device-connector-web-interfaces>`_.
The methods in this module are named in compliance with the <TODO: Insert link> naming scheme.

To use this module you will need to do the following

Install
-------
Install the ``mdc_api`` module from pip::

    pip install -U mdc_api

Use
---
There are 5 steps to using the library. For more detailed examples please see the Examples section.
You are **REQUIRED** to set up a notification channel (Step 3), either LongPolling or Callback URL before using any other connector services.

    1. Import connector module::

        import mdc_api
    
    2. Initialize instance with API token from your `Connector Access Keys <https://connector.mbed.com/#accesskeys>`_::

        x = mdc_api.connector("API TOKEN")
    
    3. Set notification Channel (Use LongPolling or CallbackURL / Webhook)::

        # Long Polling
        x.startLongPolling() 
        
        # Callback URL / Webhook, must be able to receive PUT messages
        x.putCallback('https://www.mywebapp.com:8080/callback') 

    4. **Optional** - Register Notification Channel handlers for various message types::

        # handle 'notifications' messages
        def updatesReceived(data):
            print("Received Update : %s", data.result)
        
        # register function with notification channel router
        x.setHandler('notifications',updateReceived)
    
    5. Use the API functions to access Endpoints / Resources::

        x.getEndpoints()    # get list of all endpoints on domain
        x.getResources("Endpoint") # get list of all resources on endpoint
        x.getResourceValue("Endpoint","Resource")   # get value of Resource
        x.putResourceValue("Endpoint","Resource","Data")    # set value of resource
        x.postResource("Endpoint","Resource","OptionalData")    # trigger execution funtion of resource
    
    **NOTE**: All API functions return asyncResult objects and throw connectorError objects
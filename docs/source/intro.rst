=====
Intro
=====

The mdc-api-python module is an interface between a python application and the `connector.mbed.com REST API <https://docs.mbed.com/docs/mbed-device-connector-web-interfaces>`_. This module enables you to write python programs that use mbed Device Connector. All features of the mbed Device Connector REST interface are exposed through this package. 

Requirements
-------------
    1. Python 2.7.9+ 
    2. [connector.mbed.com](http://www.connector.mbed.com) account


Install
-------
Install the ``mdc_api`` module from pip::

    pip install -U mdc_api

or install the module from [the github repo](http://www.github.com/armmbed/mbed-connector-python)::

    python setup.py install

Use
---
There are five steps to using the library. For more detailed examples please see the [Examples](./Examples) section.

You are **required** to set up a notification channel (step 3), either long polling or callback URL, before using any other mbed Device Connector services.

    1. Import the package::

        import mdc_api
    
    2. Initialize an instance with an API token from your `Connector Access Keys <https://connector.mbed.com/#accesskeys>`_::

        x = mdc_api.connector("API TOKEN")
    
    3. Set a notification channel (use long polling,  or callback URL or a webhook)::

        # Long polling
        x.startLongPolling() 
        
        # Callback URL or webhook must be able to receive PUT messages
        x.putCallback('https://www.mywebapp.com:8080/callback') 

    4. (**Optional**) Register notification channel handlers for various message types::

        # Handle 'notifications' messages
        def updatesReceived(data):
            print("Received Update : %s", data.result)
        
        # Register function with notification channel router
        x.setHandler('notifications',updateReceived)
    
    5. Use the API functions to access endpoints and resources::

        x.getEndpoints()    # Get list of all endpoints on domain
        x.getResources("Endpoint") # Get list of all resources on endpoint
        x.getResourceValue("Endpoint","Resource")   # Get value of resource
        x.putResourceValue("Endpoint","Resource","Data")    # Set value of resource
        x.postResource("Endpoint","Resource","OptionalData")    # Trigger execution function of resource
    
    **NOTE**: All API functions return asyncResult objects and throw connectorError objects.
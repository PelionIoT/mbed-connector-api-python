Intro
=====

The mbed-connector-python module is an interface to the connector.mbed.com REST API.
The methods in this module are named in compliance with the <TODO: Insert link> naming scheme.

To use this module you will need to do the following

Install
-------
Install the `mbed-connector` module from pip::

    pip install -U mbed-connector
    
Use
---
In your code import the module and instantiate it::

    from mbed-connector import connector
    x = connector(<API TOKEN>)
    x.getEndpoints()
    
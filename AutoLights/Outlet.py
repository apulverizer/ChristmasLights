#!/usr/bin/python
""" Outlet.py
    A simple outlet class
"""

class Outlet:
    id = 0 # unique identifier
    pin = 0 # pin number 
    description = "" # description
    status = 0 # on/off (1/0)

    def __init__(self, id, pin, description, status):
        self.id = id
        self.pin = pin
        self.description = description
        self.status = status

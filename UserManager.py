#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ConsMaster UserManager.
This file is part of ConsMaster.
"""

from EntityManager import *
from NetworkCodes import *

def register(username, password, email):
    if len(urep.findByUsername(username)) > 0:
        return REGISTER_ERROR_USERNAME_EXISTS
    user = User(username, password, email)
    em.add(user)
    em.commit()
    return REGISTER_SUCCESS

def authenticate(username, password):
    if len(urep.findByUsernameAndPassword(username, password)) == 1:
        return AUTHENTICATE_SUCCESS

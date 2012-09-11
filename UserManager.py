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
        return REGISTER_USERNAME_EXISTS
    user = User(username, password, email)
    em.add(user)
    return REGISTER_SUCCESS

def authenticate(username, password):
    users = urep.findByUsernameAndPassword(username, password)
    if len(users) == 1:
        return AUTHENTICATE_SUCCESS, users[0]
    else:
        return AUTHENTICATE_FAILURE, None

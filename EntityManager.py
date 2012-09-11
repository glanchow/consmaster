#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ConsMaster Database.
This file is part of ConsMaster.
"""

DB = "sqlite:///consmaster.db"

import sys
from datetime import timedelta

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String, Interval
    from sqlalchemy import ForeignKey
    from sqlalchemy.orm import relationship, backref
except:
    print >> sys.stderr, "Error:", "This program needs SQLAlchemy module."
    sys.exit(1)


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    username = Column(String, nullable = False, unique = True)
    password = Column(String)
    email = Column(String)
    scores = relationship("Score", cascade = "all, delete-orphan", \
                          backref = backref("user", order_by = id))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return "<User('%s')>" % (self.username)


class UserRepository():

    def findAll(self):
        return em.query(User).all()

    def findByUsername(self, username):
        return em.query(User).filter(User.username == username).all()

    def findByUsernameAndPassword(self, username, password):
        return em.query(User). \
               filter(User.username == username). \
               filter(User.password == password).all()


class Exercice(Base):
    __tablename__ = 'exercice'
    id = Column(Integer, primary_key = True)
    lisp = Column(String, nullable = False)
    scores = relationship("Score", cascade = "all, delete-orphan", \
                          backref = backref("exercice", order_by = id))

    def __init__(self, lisp, mode = "default"):
        self.lisp = lisp
        self.mode = mode

    def __repr__(self):
        return "<Exercice('%s')>" % (self.lisp)


class ExerciceRepository():

    def findAll(self):
        return em.query(Exercice).all()


class Score(Base):
    __tablename__ = 'Score'
    user_id = Column(Integer, ForeignKey("user.id"), primary_key = True)
    exercice_id = Column(Integer, ForeignKey("exercice.id"), primary_key = True)
    time = Column(Interval, nullable = False)
    #exercice = relationship(Exercice, lazy="joined")

    def __init__(self, exercice, time):
        self.exercice = exercice
        self.time = time

    def __repr__(self):
        return "<Score('%s')>" % (self.time)


# Let's create the entity manager at global scope.
# In python, a module is loaded only once.

engine = create_engine(DB, echo=False)

# Create tables if they don't exist.
Base.metadata.create_all(engine)

# Session is the standard name used by SQLAlchemy.
#Session = sessionmaker(bind=engine)
#session = Session()

# But here we use another name.
EntityManager = scoped_session(sessionmaker(bind=engine, autocommit=True, autoflush=True))
em = EntityManager()
urep = UserRepository()
erep = ExerciceRepository()

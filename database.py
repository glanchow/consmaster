#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ConsMaster Database.
This file is part of ConsMaster.
"""

DB = "sqlite:///consmaster.db"

import sys

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String
except:
    print >> sys.stderr, "Error:", "This program needs SQLAlchemy module."
    sys.exit(1)


engine = create_engine(DB, echo=False)

Base = declarative_base()
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
#scoped_session?

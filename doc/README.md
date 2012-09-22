consmaster
==========

Consmaster

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Current development](#development)
4. [Network](#network)
5. [Create an exercice](#exercice)
6. [Todo](#todo)


<a name="introduction"/>
1. Introduction
---------------

![consmaster screenshot](https://raw.github.com/glanchow/consmaster/master/doc/screenshot.jpg)


<a name="installation"/>
2. Installation
---------------

You will need PySide and SqlAlchemy

    $ sudo apt-get install python-pyside
    $ sudo apt-get install python-sqlalchemy
    $ git clone https://github.com/glanchow/consmaster.git

Start the client

    $ cd consmaster/src/
    $ ./consmaster.py

Start the server

    $ ./consmaster-server.py


<a name="development"/>
3. Current development
----------------------




<a name="network"/>
4. Network
----------

The network interface is based on the PySide network library.
It is fully functionnal although at the time I'm writing it only supports register and login commands.
I'm going to describe the login command so that you can add your own commands.

By default you can connect to the server as an anonymous user, and after that you can use a simple command to login as a user.

Let's look on the server side.

    # src consmaster-server.py
    self.user = None
    self.commands = {}
    self.commands["register"] = self.register
    self.commands["login"] = self.login

The server handles each client with a single thread, and every thread knows it's user as self.user, which is None if the user is connected as anonymous.
Then each command is referenced by it's name in the commands dict, with the corresponding routine.

    # src consmaster-server.py
    def login(self, inStream):
        username = inStream.readQString()
        password = inStream.readQString()
        email = inStream.readQString()
        status, user = UserManager.authenticate(username, password)
        if status == AUTHENTICATE_SUCCESS:
            self.user = user
        reply, outStream = self.newReply()
        outStream.writeInt16(status)
        self.sendReply(reply, outStream)

The request looks like « register username password email » but in a binary format understood by PySide, this is why we use builtins like readQString(), to detect words encoded with writeQString() as we will see in a few lines.
The reply starts with a status code and whatever you want after that.
You can have a look at status code :

    # src NetworkCodes.py
    REGISTER_SUCCESS = 300
    REGISTER_USERNAME_EXISTS = 301
    AUTHENTICATE_SUCCESS = 400
    AUTHENTICATE_FAILURE = 401

Then in the client, a routine is dedicated to each reply.

     # src consmaster.py
     self.replies = {}
     self.replies[REGISTER_SUCCESS] = self.registered
     self.replies[REGISTER_USERNAME_EXISTS] = self.alreadyRegistered
     self.replies[AUTHENTICATE_SUCCESS] = self.logged
     self.replies[AUTHENTICATE_FAILURE] = self.badCreditentials

And finally here's how we send a command from the client to the server.

    # src consmaster.py
    def login(self):
        request, outStream = self.newRequest()
        outStream.writeQString("login")
        outStream.writeQString(self.usernameLineEdit.text())
        outStream.writeQString(self.passwordLineEdit.text())
        self.sendRequest(request, outStream)

<a name="exercice"/>
5. Exercice
---------------

Take a look at solver.py


<a name="todo"/>
6. Todo
-------

1. Let the user choose host and port from command line for both client and server
2. Store host, port, and other configuration in a config file like ~/.consmasterrc
3. Find a good daemonizer script for the server
4. Check for non linear graph drawing in Pigale project to draw good looking conses

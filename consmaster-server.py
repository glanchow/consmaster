#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ConsMaster server.
This file is part of ConsMaster.
"""

PORT = 54454
SIZEOF_UINT16 = 2

import sys
import signal
import EntityManager
import UserManager

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtNetwork import *
except:
    print >> sys.stderr, "Error:", "This program needs PySide module."
    sys.exit(1)


class Thread(QThread):

    error = Signal(QTcpSocket.SocketError)
    lock = QReadWriteLock()

    def __init__(self, socketDescriptor, parent):
        super(Thread, self).__init__(parent)
        self.socketDescriptor = socketDescriptor
        self.reply = None
        self.commands = {}
        self.commands["register"] = self.register

    def run(self):
        self.socket = QTcpSocket()
        if not self.socket.setSocketDescriptor(self.socketDescriptor):
            self.error.emit(self.socket.error())
            return
        while self.socket.state() == QAbstractSocket.ConnectedState:
            nextBlockSize = 0
            inStream = QDataStream(self.socket)
            inStream.setVersion(QDataStream.Qt_4_2)
            while True:
                self.socket.waitForReadyRead(-1)
                if self.socket.bytesAvailable() >= SIZEOF_UINT16:
                    nextBlockSize = inStream.readUInt16()
                    break
            if self.socket.bytesAvailable() < nextBlockSize:
                while True:
                    self.socket.waitForReadyRead(-1)
                    if self.socket.bytesAvailable() >= nextBlockSize:
                        break

            command = inStream.readQString()
            print "Received command", command
            self.commands[command](inStream)

    def sendError(self, msg):
        self.newReply()
        self.outStream.writeQString("ERROR")
        self.outStream.writeQString(msg)
        self.sendReply()

    def newReply(self):
        while self.reply != None:
            pass
        self.reply = QByteArray()
        self.outStream = QDataStream(self.reply, QIODevice.WriteOnly)
        self.outStream.setVersion(QDataStream.Qt_4_2)
        self.outStream.writeUInt16(0)

    def sendReply(self):
        self.outStream.device().seek(0)
        self.outStream.writeUInt16(self.reply.size() - SIZEOF_UINT16)
        self.socket.write(self.reply)
        self.reply = None

    def register(self, inStream):
        username = inStream.readQString()
        password = inStream.readQString()
        email = inStream.readQString()
        print "Register", username, password, email
        registered = UserManager.register(username, password, email)
        self.newReply()
        self.outStream.writeInt16(registered)
        self.sendReply()
        #UserManager.authenticate(username, password)
        #UserManager.register("test", password, "emailtest")
        #UserManager.resetPassword(email)


class Server(QTcpServer):

    def __init__(self):
        super(Server, self).__init__()
        if not self.listen(QHostAddress("0.0.0.0"), PORT):
            print >> sys.stderr, "Failed to start server: ", self.errorString()
            sys.exit(1)

    def incomingConnection(self, socketDescriptor):
        print "Incoming connection"
        thread = Thread(socketDescriptor, self)
        thread.finished.connect(thread.deleteLater)
        thread.start()

if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal.SIG_DFL) # Terminate with ^C

    app = QCoreApplication(sys.argv)
    server = Server()
    sys.exit(app.exec_())

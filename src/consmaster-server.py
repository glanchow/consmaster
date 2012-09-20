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
from EntityManager import *
from NetworkCodes import *
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

    def __init__(self, socketDescriptor, parent):
        super(Thread, self).__init__(parent)
        self.socketDescriptor = socketDescriptor
        self.user = None
        self.commands = {}
        self.commands["register"] = self.register
        self.commands["login"] = self.login

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
            self.commands[command](inStream)

    def newReply(self):
        reply = QByteArray()
        outStream = QDataStream(reply, QIODevice.WriteOnly)
        outStream.setVersion(QDataStream.Qt_4_2)
        outStream.writeUInt16(0)
        return reply, outStream

    def sendReply(self, reply, outStream):
        outStream.device().seek(0)
        outStream.device().seek(0)
        outStream.writeUInt16(reply.size() - SIZEOF_UINT16)
        self.socket.write(reply)

    def register(self, inStream):
        username = inStream.readQString()
        password = inStream.readQString()
        email = inStream.readQString()
        status = UserManager.register(username, password, email)
        reply, outStream = self.newReply()
        outStream.writeInt16(status)
        self.sendReply(reply, outStream)

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


class Server(QTcpServer):

    def __init__(self):
        super(Server, self).__init__()
        if not self.listen(QHostAddress("0.0.0.0"), PORT):
            print >> sys.stderr, "Failed to start server: ", self.errorString()
            sys.exit(1)

    def incomingConnection(self, socketDescriptor):
        thread = Thread(socketDescriptor, self)
        thread.finished.connect(thread.deleteLater)
        thread.start()

if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal.SIG_DFL) # Terminate with ^C

    app = QCoreApplication(sys.argv)
    server = Server()
    sys.exit(app.exec_())

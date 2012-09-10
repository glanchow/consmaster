#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ConsMaster client.
This file is part of ConsMaster.
"""

HOST = "localhost"
PORT = "54454"
SIZEOF_UINT16 = 2

import sys
import signal
from glisp import *
from NetworkCodes import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtNetwork import *
except:
    print >> sys.stderr, "Error:", "This program needs PySide module."
    sys.exit(1)


class Client(QMainWindow):
    """Client."""

    def __init__(self, parent=None):
        super(Client, self).__init__(parent)

        self.socket = QTcpSocket()

        self.socket.connected.connect(self.connected)
        self.socket.disconnected.connect(self.disconnected)
        self.socket.error.connect(self.socketError)
        self.socket.readyRead.connect(self.readReply)

        self.request = None
        self.onReplies = {}
        self.onReplies["registered"] = self.registered

        self.createActions()
        self.createMenus()
        self.createToolBar()

        self.createConnectDialog()
        self.createRegisterDialog()
        self.createLoginDialog()

        self.createWorkWidget()

        self.setCentralWidget(self.workWidget)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("ConsMaster")
        self.show()

        #self.connect()


    #
    # SERVER COMMUNICATION AND EVENTS
    #

    def connect(self):
        if self.socket.isOpen():
            self.socket.close()

        self.host = self.hostLineEdit.text()
        self.port = int(self.portLineEdit.text())
        self.statusBar().showMessage(u"Connecting to server…")
        self.socket.connectToHost(self.host, self.port)

    def disconnect(self):
        self.socket.close()

    def connected(self):
        self.hideConnectDialog()
        self.statusBar().showMessage(u"Connecté")
        self.connectAction.setEnabled(False)
        self.disconnectAction.setEnabled(True)
        self.loginAction.setEnabled(True)
        self.registerAction.setEnabled(True)

    def disconnected(self):
        self.statusBar().showMessage(u"Déconnecté")
        self.connectAction.setEnabled(True)
        self.disconnectAction.setEnabled(False)
        self.anonymousAction.setEnabled(False)
        self.loginAction.setEnabled(False)
        self.registerAction.setEnabled(False)

    def socketError(self, socketError):
        q = QMessageBox(self)
        q.setWindowTitle(u"Erreur réseau")
        q.setIconPixmap(QPixmap("icons/network-error.png"))
        q.show()

        if socketError == QAbstractSocket.RemoteHostClosedError:
            q.setText(u"Le serveur a terminé la connexion.")
        elif socketError == QAbstractSocket.HostNotFoundError:
            q.setText(u"Hôte introuvable. Vérifier les paramètres de connexion.")
        elif socketError == QAbstractSocket.ConnectionRefusedError:
            q.setText(u"Connexion refusée. Vérifier que le serveur existe.")
        else:
            q.setText(u"Erreur: %s." % self.socket.errorString())

    def newRequest(self):
        while self.request != None:
            pass
        self.request = QByteArray()
        self.outStream = QDataStream(self.request, QIODevice.WriteOnly)
        self.outStream.setVersion(QDataStream.Qt_4_2)
        self.outStream.writeUInt16(0)

    def sendRequest(self):
        self.outStream.device().seek(0)
        self.outStream.writeUInt16(self.request.size() - SIZEOF_UINT16)
        self.socket.write(self.request)
        self.request = None

    def readReply(self):
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

        onReply = inStream.readQString()
        print "Received reply", onReply
        self.onReplies[onReply](inStream)

    #
    # SERVER COMMANDS
    #

    def register(self):
        self.newRequest()
        self.outStream.writeQString("register")
        self.outStream.writeQString(self.username2LineEdit.text())
        self.outStream.writeQString(self.password2LineEdit.text())
        self.outStream.writeQString(self.email2LineEdit.text())
        self.sendRequest()

    def registered(self, inStream):
        status = inStream.readInt16()
        if status == REGISTER_SUCCESS:
            self.statusBar().showMessage(u"Inscription réussie")
        elif status == REGISTER_ERROR_USERNAME_EXISTS:
            self.statusBar().showMessage(u"Inscription interrompue, nom d'utilisateur existant")

    def login():
        pass

    def createActions(self):
        self.connectAction = QAction(QIcon("icons/network-idle"),
                u"&Connexion", self, shortcut="Ctrl+Shift+C", enabled=True,
                statusTip=u"Connexion au serveur", triggered=self.showConnectDialog)
        self.disconnectAction = QAction(QIcon("icons/network-offline"),
                u"&Déconnexion", self, shortcut="Ctrl+Shift+D", enabled=False,
                statusTip=u"Déconnexion du serveur", triggered=self.disconnect)
        self.anonymousAction = QAction(QIcon("icons/kuser"),
                u"&Anonyme", self, shortcut="Ctrl+Shift+N", enabled=False,
#Todo
#                checkable=True, checked=True,
                statusTip=u"Utilisateur anonyme", triggered=self.todo)
        self.loginAction = QAction(QIcon("icons/kgpg"),
                u"&Authentification", self, shortcut="Ctrl+Shift+A", enabled=False,
#                checkable=True, checked=False,
                statusTip=u"Utilisateur authentifié", triggered=self.showLoginDialog)
        self.registerAction = QAction(QIcon("icons/key-single"),
                u"&Inscription", self, shortcut="Ctrl+Shift+I", enabled=False,
                statusTip=u"Créer un compte", triggered=self.showRegisterDialog)
        self.passwordAction = QAction(QIcon("icons/mail-reply-sender"),
                u"&Récupération", self, shortcut="Ctrl+Shift+R", enabled=False,
                statusTip=u"Renvoyer le mot de passe sur l'email", triggered=self.todo)
        self.quitAction = QAction(QIcon("icons/application-exit"),
                u"&Quitter", self, shortcut="Ctrl+Shift+Q",
                statusTip=u"Quitter l'application", triggered=self.close)
        self.aboutAction = QAction(QIcon("icons/help-browser"),
                u"A &propos", self, shortcut="Ctrl+Shift+P",
                triggered=self.about)

    def createMenus(self):
        self.clientMenu = self.menuBar().addMenu(u"&Client")
        self.clientMenu.addAction(self.connectAction)
        self.clientMenu.addAction(self.disconnectAction)
        self.clientMenu.addSeparator()
        self.clientMenu.addAction(self.anonymousAction)
        self.clientMenu.addAction(self.loginAction)
        self.clientMenu.addAction(self.registerAction)
        self.clientMenu.addAction(self.passwordAction)
        self.clientMenu.addSeparator()
        self.clientMenu.addAction(self.quitAction)

        self.aboutMenu = self.menuBar().addMenu(u"&Aide")
        self.aboutMenu.addAction(self.aboutAction)

    def createToolBar(self):

        self.toolbar = self.addToolBar(u"Navigation")
        self.toolbar.setMovable(False)
        self.toolbar.addAction(self.connectAction)
        self.toolbar.addAction(self.disconnectAction)
        self.toolbar.addAction(self.loginAction)

    def createWorkWidget(self):
        workWidget = QWidget()
        self.workWidget = workWidget
        glispWidget = GLispWidget(self)
        self.glisp = glispWidget.glisp
        self.addToolBar(self.glisp.toolBar)
        print self.glisp.rep("(setq l (quote (a b c)))")
#        self.glisp.clear()
#        self.glisp.display("l")
#        self.glisp.evalAndDisplay("l")

#        print self.glisp.repg("(setq liste (quote (a)))")
#        print self.glisp.rep("(setq liste (quote (a)))")
#        print self.glisp.repg("l")
#        print self.glisp.rep("(a b c)")
        #test
#        lisp = Lisp()
#        print lisp.rep("(setq l (quote (a b c)))")
#        print lisp.rep("l")
        #endtest
        lispLabel = QLabel(u"&Lisp:")
        dottedLabel = QLabel(u"&Dotted:")
        self.lispLineEdit = QLineEdit("")
        self.dottedLineEdit = QLineEdit("")
        self.dottedLineEdit.setFocus()
        lispLabel.setBuddy(self.lispLineEdit)
        dottedLabel.setBuddy(self.dottedLineEdit)
        self.responseLabel = QLabel(u"")
        self.submitWorkButton = QPushButton(u"Valider")
        self.submitWorkButton.setDefault(True)
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.submitWorkButton, QDialogButtonBox.ActionRole)
        #self.lispLineEdit.textChanged.connect(self.updateConnectButton)
        #self.dottedLineEdit.textChanged.connect(self.updateConnectButton)
        self.submitWorkButton.clicked.connect(self.submitWork)
        layout = QGridLayout()
        layout.addWidget(glispWidget, 0, 0, 1, 2)
        layout.addWidget(lispLabel, 1, 0)
        layout.addWidget(self.lispLineEdit, 1, 1)
        layout.addWidget(dottedLabel, 2, 0)
        layout.addWidget(self.dottedLineEdit, 2, 1)
        layout.addWidget(self.responseLabel, 3, 0, 1, 2)
        layout.addWidget(buttonBox, 4, 0, 1, 2)
        workWidget.setLayout(layout)

    def submitWork(self):
        print self.lispLineEdit.text()

    def createConnectDialog(self):
        self.connectDialog = QDialog()
        self.connectDialog.setModal(True)
        self.connectDialog.setWindowTitle(u"Connexion")

        self.hostLineEdit = QLineEdit(HOST)
        self.hostLineEdit.setFocus()
        self.portLineEdit = QLineEdit(PORT)
        self.portLineEdit.setValidator(QIntValidator(1, 65535, self))

        self.hostLineEdit.textChanged.connect(self.updateConnectButton)
        self.portLineEdit.textChanged.connect(self.updateConnectButton)

        self.connectButton = QPushButton(u"Connexion")
        self.connectButton.setDefault(True)
        cancelButton = QPushButton(u"Annuler")
        self.updateConnectButton()

        self.connectButton.clicked.connect(self.connect)
        cancelButton.clicked.connect(self.hideConnectDialog)

        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.connectButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)

        form = QFormLayout()
        form.addRow(u"&Serveur :", self.hostLineEdit)
        form.addRow(u"&Port :", self.portLineEdit)
        form.addRow(buttonBox)

        self.connectDialog.setLayout(form)

    def hideConnectDialog(self):
        self.connectDialog.hide()

    def showConnectDialog(self):
        self.connectDialog.show()

    def updateConnectButton(self):
        self.connectButton.setEnabled(False)
        if self.hostLineEdit.text() and self.portLineEdit.text():
            self.connectButton.setEnabled(True)

    def createRegisterDialog(self):
        self.registerDialog = QDialog()
        self.registerDialog.setModal(True)
        self.registerDialog.setWindowTitle(u"Inscription")

        self.username2LineEdit = QLineEdit()
        self.username2LineEdit.setFocus()
        self.email2LineEdit = QLineEdit()
        self.password2LineEdit = QLineEdit()

        self.username2LineEdit.textChanged.connect(self.updateRegisterButton)
        self.email2LineEdit.textChanged.connect(self.updateRegisterButton)
        self.password2LineEdit.textChanged.connect(self.updateRegisterButton)

        self.registerButton = QPushButton(u"Inscription")
        self.registerButton.setDefault(True)
        cancelButton = QPushButton(u"Annuler")
        self.updateRegisterButton()

        self.registerButton.clicked.connect(self.register)
        cancelButton.clicked.connect(self.hideRegisterDialog)

        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.registerButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)

        form = QFormLayout()
        form.addRow(u"&Nom d'utilisateur :", self.username2LineEdit)
        form.addRow(u"&Mot de passe :", self.password2LineEdit)
        form.addRow(u"&Adresse email :", self.email2LineEdit)
        form.addRow(buttonBox)

        self.registerDialog.setLayout(form)

    def hideRegisterDialog(self):
        self.registerDialog.hide()

    def showRegisterDialog(self):
        self.registerDialog.show()

    def updateRegisterButton(self):
        self.registerButton.setEnabled(False)
        if self.username2LineEdit.text() and self.email2LineEdit.text() \
               and self.password2LineEdit.text():
            self.registerButton.setEnabled(True)

    def createLoginDialog(self):
        self.loginDialog = QDialog()
        self.loginDialog.setModal(True)
        self.loginDialog.setWindowTitle(u"Inscription")

        self.usernameLineEdit = QLineEdit()
        self.usernameLineEdit.setFocus()
        self.passwordLineEdit = QLineEdit()

        self.usernameLineEdit.textChanged.connect(self.updateLoginButton)
        self.passwordLineEdit.textChanged.connect(self.updateLoginButton)

        self.loginButton = QPushButton(u"Authentification")
        self.loginButton.setDefault(True)
        cancelButton = QPushButton(u"Annuler")
        self.updateLoginButton()

        self.loginButton.clicked.connect(self.login)
        cancelButton.clicked.connect(self.hideLoginDialog)

        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.loginButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.RejectRole)

        form = QFormLayout()
        form.addRow(u"&Nom d'utilisateur :", self.usernameLineEdit)
        form.addRow(u"&Mot de passe :", self.passwordLineEdit)
        form.addRow(buttonBox)

        self.loginDialog.setLayout(form)

    def hideLoginDialog(self):
        self.loginDialog.hide()

    def showLoginDialog(self):
        self.loginDialog.show()

    def updateLoginButton(self):
        self.loginButton.setEnabled(False)
        if self.usernameLineEdit.text() and self.passwordLineEdit.text():
            self.loginButton.setEnabled(True)

    def todo(self):
        QMessageBox.about(self, "Todo", u"Cette fonctionnalité sera ajoutée prochaînement.")

    def about(self):
        QMessageBox.about(self, "A propos ConsMaster",
                u"Maîtrisez les représentations de listes, en notations parenthésées, à point et en doublets graphiques.")


if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal.SIG_DFL) # Terminate with ^C

    app = QApplication(sys.argv)
    client = Client()
    sys.exit(app.exec_())

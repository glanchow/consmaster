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

        self.socket = QTcpSocket()
        self.nextBlockSize = 0

        self.socket.connected.connect(self.connected)
        self.socket.disconnected.connect(self.disconnected)
        self.socket.error.connect(self.socketError)
        self.socket.readyRead.connect(self.readReply)

        self.replies = {}
        self.replies[REGISTER_SUCCESS] = self.registered
        self.replies[REGISTER_USERNAME_EXISTS] = self.alreadyRegistered
        self.replies[AUTHENTICATE_SUCCESS] = self.logged
        self.replies[AUTHENTICATE_FAILURE] = self.badCreditentials

        #self.connect()

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
        self.workWidget = QWidget()

        glispLabel = QLabel(u"&Représentation graphique:")
        lispLabel = QLabel(u"&Représentation parenthésée:")
        dottedLabel = QLabel(u"&Représentation à point:")

        glispWidget = GLispWidget(self)
        self.glisp = glispWidget.glisp
        self.glisp.clear()
        self.addToolBar(self.glisp.toolBar)

        self.glisp.rep("(setq liste (quote (a b c)))")
        self.glisp.clear()
        self.glisp.display("liste")
        self.glisp.evalAndDisplay("liste")

#        print self.glisp.repg("(setq liste (quote (a)))")
#        print self.glisp.rep("(setq liste (quote (a)))")
#        print self.glisp.repg("l")
#        print self.glisp.rep("(a b c)")
        #tes
#        lisp = Lisp()
#        print lisp.rep("(setq l (quote (a b c)))")
#        print lisp.rep("l")
        #endtest

        self.lispLineEdit = QLineEdit("")
        self.lispLineEdit.setFocus()
        self.dottedLineEdit = QLineEdit("")

        glispLabel.setBuddy(glispWidget)
        lispLabel.setBuddy(self.lispLineEdit)
        dottedLabel.setBuddy(self.dottedLineEdit)

        translateFromGraphicsButton = QPushButton(u"Traduire")
        translateFromLispButton = QPushButton(u"Traduire")
        translateFromDottedButton = QPushButton(u"Traduire")

        translateFromGraphicsButton.clicked.connect(self.translateFromGraphics)
        translateFromLispButton.clicked.connect(self.translateFromLisp)
        translateFromDottedButton.clicked.connect(self.translateFromDotted)

        layout = QGridLayout()
        layout.addWidget(glispLabel, 0, 0, 1, 2)
        layout.addWidget(glispWidget, 1, 0, 1, 2)
        layout.addWidget(translateFromGraphicsButton, 2, 1, 1, 2, Qt.AlignRight)
        layout.addWidget(lispLabel, 3, 0)
        layout.addWidget(self.lispLineEdit, 3, 1)
        layout.addWidget(translateFromLispButton, 4, 1, 1, 2, Qt.AlignRight)
        layout.addWidget(dottedLabel, 5, 0)
        layout.addWidget(self.dottedLineEdit, 5, 1)
        layout.addWidget(translateFromDottedButton, 6, 1, 1, 2, Qt.AlignRight)
        self.workWidget.setLayout(layout)

    def translateFromGraphics(self):
        self.lispLineEdit.setText(self.glisp.rep("liste"))
        self.dottedLineEdit.setText(self.glisp.red("liste"))

    def translateFromLisp(self):
        self.glisp.rep("(setq liste (quote "+self.lispLineEdit.text()+"))")
        self.glisp.clear()
        self.glisp.display("liste")
        self.glisp.evalAndDisplay("liste")
        self.dottedLineEdit.setText(self.glisp.red("liste"))

    def translateFromDotted(self):
        self.glisp.rep("(setq liste (quote "+self.dottedLineEdit.text()+"))")
        self.glisp.clear()
        self.glisp.display("liste")
        self.glisp.evalAndDisplay("liste")
        self.lispLineEdit.setText(self.glisp.rep("liste"))

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
        self.loginDialog.setWindowTitle(u"Authentification")

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

    #
    # NETWORK MANAGMENT
    #

    def connect(self):
        if self.socket.isOpen():
            self.socket.close()

        self.host = self.hostLineEdit.text()
        self.port = int(self.portLineEdit.text())
        self.statusBar().showMessage(u"Connexion…")
        self.socket.connectToHost(self.host, self.port)

    def disconnect(self):
        self.socket.close()

    def connected(self):
        self.hideConnectDialog()
        self.statusBar().showMessage(u"Connecté.")
        self.connectAction.setEnabled(False)
        self.disconnectAction.setEnabled(True)
        self.loginAction.setEnabled(True)
        self.registerAction.setEnabled(True)

    def disconnected(self):
        self.statusBar().showMessage(u"Déconnecté.")
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
        request = QByteArray()
        outStream = QDataStream(request, QIODevice.WriteOnly)
        outStream.setVersion(QDataStream.Qt_4_2)
        outStream.writeUInt16(0)
        return request, outStream

    def sendRequest(self, request, outStream):
        outStream.device().seek(0)
        outStream.writeUInt16(request.size() - SIZEOF_UINT16)
        self.socket.write(request)

    def readReply(self):
        inStream = QDataStream(self.socket)
        inStream.setVersion(QDataStream.Qt_4_2)
        if self.nextBlockSize == 0:
            if self.socket.bytesAvailable() < SIZEOF_UINT16:
                return
            self.nextBlockSize = inStream.readUInt16()
        if self.socket.bytesAvailable() < self.nextBlockSize:
            return
        replyCode = inStream.readInt16()
        self.replies[replyCode](inStream)
        self.nextBlockSize = 0

    #
    # SERVER COMMANDS AND REPLIES
    #

    def successMessage(self, message, title=None):
        if title == None:
            title = u"Succès"
        q = QMessageBox(self)
        q.setWindowTitle(title)
        q.setIconPixmap(QPixmap("icons/button_accept"))
        q.setText(message)
        q.show()

    def errorMessage(self, message, title=None):
        if title == None:
            title = u"Erreur"
        q = QMessageBox(self)
        q.setWindowTitle(title)
        q.setIconPixmap(QPixmap("icons/user-busy.png"))
        q.setText(message)
        q.show()

    def register(self):
        request, outStream = self.newRequest()
        outStream.writeQString("register")
        outStream.writeQString(self.username2LineEdit.text())
        outStream.writeQString(self.password2LineEdit.text())
        outStream.writeQString(self.email2LineEdit.text())
        self.sendRequest(request, outStream)

    def registered(self, inStream):
        self.registerDialog.hide()
        self.successMessage(u"Inscription réussie.")

    def alreadyRegistered(self, inStream):
        self.errorMessage(u"Le nom d'utilisateur existe déjà sur ce serveur.")

    def login(self):
        request, outStream = self.newRequest()
        outStream.writeQString("login")
        outStream.writeQString(self.usernameLineEdit.text())
        outStream.writeQString(self.passwordLineEdit.text())
        self.sendRequest(request, outStream)

    def logged(self, inStream):
        self.loginDialog.hide()
        self.statusBar().showMessage(u"Authentifié.")
        self.loginAction.setEnabled(False)

    def badCreditentials(self, inStream):
        self.errorMessage(u"Le nom d'utilisateur et le mot de passe ne correspondent pas.")


if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal.SIG_DFL) # Terminate with ^C

    app = QApplication(sys.argv)
    client = Client()
    sys.exit(app.exec_())

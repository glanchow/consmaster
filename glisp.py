#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
from lisp import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print >> sys.stderr, "Error:", "This program needs PySide module."
    sys.exit(1)


class Arrow(QGraphicsLineItem):
    """Arrow.

    An Arrow serves as drawing for Pointer.
    An arrow is basically linking a start point and an end point.
    The body is made of a line between those points.
    The base with  a little ellipse.
    The head with a little triangle.

    Args:
        p1: start QPointF
        p2: end QPointF
    """

    baseSize = 6
    bodySize = 2
    headSize = 12
    penColor = Qt.black
    base = QRectF()
    head = QPolygonF()

    def __init__(self, p1, p2, parent=None, scene=None):
        super(Arrow, self).__init__(parent, scene)
        self.base = QRectF(p1.x() - self.baseSize / 2,
                           p1.y() - self.baseSize / 2,
                           self.baseSize, self.baseSize)
        self.setLine(QLineF(p1, p2))
        # Add this when you add the remove action for Pointers
        #self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setPen(QPen(self.penColor, self.bodySize, Qt.SolidLine))

    def boundingRect(self):
        # The boundingRect is used to refresh the view display
        # We must set the boundingRect of our Arrow accordingly with the size
        # of the elements we added to this line item : the base and head
        extra = (self.pen().width() + self.headSize) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).\
               normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        # The shape is used to detect collisions and receive mouse clicks
        # We must set the shape of our Arrow accordingly with the shape
        # of the elements we added to this line item : the base and head
        path = super(Arrow, self).shape()
        path.addRect(self.base)
        path.addPolygon(self.head)
        return path

    def paint(self, painter, option, widget=None):
        # We have to tell the view how to paint an arrow
        # Firstly the base, then the body and finally the head
        self.pen().setColor(self.penColor)
        painter.setPen(self.pen())
        painter.setBrush(self.penColor)

        # Paint the base ellipse
        painter.drawEllipse(self.base)

        # Paint the body
        body = self.line()
        if body.length() == 0:
            return
        painter.drawLine(body)

        # Paint the head
        if body.length() < self.headSize:
            headSize = body.length()
        else:
            headSize = self.headSize
        angle = math.acos(body.dx() / body.length())
        if body.dy() >= 0:
            angle = (math.pi * 2.0) - angle
        v1 = body.p2() - QPointF(math.sin(angle + math.pi / 3.0) * headSize,
                                 math.cos(angle + math.pi / 3.0) * headSize)
        v2 = body.p2() - QPointF(math.sin(angle + math.pi - math.pi / 3.0) * headSize,
                                 math.cos(angle + math.pi - math.pi / 3.0) * headSize)
        head = QPolygonF()
        for vertex in [body.p2(), v1, v2]:
            head.append(vertex)
        painter.drawPolygon(head)
        self.head = head


class Pointer(Arrow):
    """Pointer.

    A Pointer is an Arrow, but linking two items.
    It knows it's start and end items so it can morph while they move.
# TODO
startItem.center devrait s'appeler arrowOffset
et cette fonction devrait être implémentée dans PointerAble par exemple
puis réimplentée par les items qui le souhaitent
#    The items must inherit from PointerAble as we use a special offset function.

    Args:
        startItem: QGraphicsItem
        endItem: QGraphicsItem
#        startItem: a PointerAble QGraphicsItem
#        endItem: a PointerAble QGraphicsItem
    """

    def __init__(self, startItem, endItem, parent=None, scene=None):
        self.startItem = startItem
        self.endItem = endItem
        self.p1 = startItem.pointerOffset + startItem.scenePos()
        self.p2 = endItem.scenePos()
        super(Pointer, self).__init__(self.p1, self.p2, parent, scene)

    def paint(self, painter, option, widget=None):
        self.p1 = self.startItem.pointerOffset + self.startItem.scenePos()
        self.p2 = self.endItem.scenePos()
        self.setLine(QLineF(self.p1, self.p2))
        super(Pointer, self).paint(painter, option, widget)


class ReferenceAble(object):
    """ReferenceAble.

    ReferenceAble gives the tools to manage a list of references to oneself.
    Symbols, Conses and other Lisp Objects may be referenced by a pointer.
    Moreover, having a list of references may be used to detect circularity,
    or free memory with a garbage collector.
    """

    #references = []

    def __init__(self, *args, **kwargs):
        super(ReferenceAble, self).__init__(*args, **kwargs)
        self.references = []
        print "ReferenceAble inited"

    def addReference(self, reference):
         self.references.append(reference)

    def removeReference(self, reference):
        try:
            self.references.remove(reference)
        except ValueError:
            pass

    def removeReferences(self):
        for reference in self.references[:]:
            reference.startItem.deletedTarget()
#            reference.endItem.removeReference(reference)
#            self.scene().removeItem(reference)


class PointerAble(QGraphicsRectItem, object):

    body = QRectF(0, 0, 15, 15)
    pointerOffset = QPointF(2, 2)
    target = None
    # Where should I point to when my target has been deleted
    defaultTarget = None
    pointer = None

    def __init__(self, target=None, parent=None, scene=None, *args, **kwargs):
        super(PointerAble, self).__init__(parent, scene, *args, **kwargs)
        print "PointerAble inited"
        self.setRect(self.body)
        self.gnil = QGraphicsLineItem(QLineF(QPointF(0, 38), QPointF(38, 0)), self)
        self.true = QGraphicsLineItem(QLineF(QPointF(0, 0), QPointF(38, 38)), self)
        if target:
            self.setTarget(target)

    def setTarget(self, obj):
        #prob avec Nil qui existe pas dans glisp.py encore
#        if not isinstance(obj, ReferenceAble):
#            return

        # Remove existing pointer
        if self.pointer:
            self.target.removeReference(self.pointer)
            self.scene().removeItem(self.pointer)
            self.pointer = None

        # Set new target
        self.target = obj
        self.gnil.hide()
        self.true.hide()

        if obj == None:
            return
        elif nilp(obj):
            self.gnil.show()
        elif tp(obj):
            self.gnil.show()
            self.true.show()
        else:
            self.pointer = Pointer(self, self.target, None, self.scene())
            self.target.addReference(self.pointer)

    def getTarget(self):
        return self.target

    def setDefaultTarget(self, target):
        self.defaultTarget = target

    def deletedTarget(self):
        self.setTarget(self.defaultTarget)


class GLispObject(ReferenceAble, LispObject, QGraphicsPolygonItem, object):
    """GLispObject."""

    contextMenu = None

    def __init__(self, parent=None, scene=None, *args, **kwargs):
        super(GLispObject, self).__init__(parent, scene, *args, **kwargs)
        print "GLispObject inited"
        print self.references
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        if self.contextMenu == None:
            return
        self.contextMenu.exec_(event.screenPos())

    def mouseDoubleClickEvent(self, event):
        self.contextMenu.defaultAction().trigger()


class GString(String, GLispObject, object):
    """GString."""
    def __init__(self, text, parent=None, scene=None, *args, **kwargs):
        super(GString, self).__init__(text, parent, scene, *args, **kwargs)
        self.textGraphic = QGraphicsTextItem(text, self)

class GSymbol(Symbol, GLispObject, object):
    """GSymbol."""

    gcval = None
    gcvalBody = QRectF(0, 0, 20, 20)
    gcvalPos = QPointF(0, 10)

    def __init__(self, pname, parent=None, scene=None, *args, **kwargs):
        super(GSymbol, self).__init__(pname, None, None, parent, scene, *args, **kwargs)
        print self, "inited"
        print isinstance(self,ReferenceAble)
        #print self.references
        self.setBrush(Qt.lightGray)
        self.gcval = PointerAble(None, self, scene)
        self.gcval.setPos(self.gcvalPos)

        self.setPolygon(QRectF(0, 0, 40, 40))
        self.pointerOffset = QPointF(20, 20)

    def setCval(self, cval):
        if self.gcval == None:
            super(GSymbol, self).setCval(cval)
            return
        self.gcval.setTarget(cval)

    def getCval(self):
        if self.gcval == None:
            super(GSymbol, self).getCval()
            return
        return self.gcval.getTarget()

    def __repr__(self):
        return "<GSymbol('%s')>" % (self.pname.text)


class GCons(Cons, GLispObject, object):
    """GCons."""

    body = QRectF(0, 0, 80, 40)
    referenceOffset = QPointF(0, 0)
    gcar = None
    gcarBody = QRectF(0, 0, 39, 38)
    gcarPointerOffset = QPointF(20, 19)
    gcdr = None
    gcdrBody = QRectF(0, 0, 39, 38)
    gcdrPointerOffset = QPointF(20, 19)

    def __init__(self, car, cdr, parent=None, scene=None, *args, **kwargs):
        super(GCons, self).__init__(None, None, parent, scene, *args, **kwargs)
        self.setPolygon(self.body)
        self.gcar = PointerAble(None, self, scene)
        self.gcar.setRect(self.gcarBody)
        self.gcar.pointerOffset = self.gcarPointerOffset
        self.gcar.defaultTarget = GLisp.nil
        self.gcar.setPos(1, 1)
        self.gcdr = PointerAble(None, self, scene)
        self.gcdr.setRect(self.gcdrBody)
        self.gcdr.pointerOffset = self.gcdrPointerOffset
        self.gcdr.defaultTarget = GLisp.nil
        self.gcdr.setPos(40, 1)
        self.setCar(car)
        self.setCdr(cdr)

    def __repr__(self):
        return "<GCons('%s, %s')>" % (self.car, self.cdr)

    def getPointerOffset(self):
        return referenceOffset

    def setCar(self, obj):
        if self.gcar == None:
            return super(GCons, self).setCar(obj)
        print "obj", obj
        return self.gcar.setTarget(obj)
    def getCar(self):
        if self.gcar == None:
            return super(GCons, self).getCar()
        return self.gcar.getTarget()
    def setCdr(self, obj):
        if self.gcdr == None:
            return super(GCons, self).setCdr(obj)
        return self.gcdr.setTarget(obj)
    def getCdr(self):
        if self.gcdr == None:
            return super(GCons, self).getCdr()
        return self.gcdr.getTarget()


class GLisp(Lisp, QGraphicsScene, object):
    # Modes are used to determine left-click action
    SelectOrMove, AddSymbol, AddCons, SetPointer = range(4)
    mode = None
    rightClickPos = None
#todo, revoir le nom des sous-classes des GObjets

    # SIGNALER les étapes des modes
    objectInserted = Signal(GLispObject)
    # mettre added plutot que insterted
    #faire pareil lorsque l'insert est cancel
    # faire un mode pour la 2ème étape du pointage
    # textInserted = Signal(QGraphicsTextItem)
    # itemSelected = Signal(QGraphicsItem)

    # A temporary Arrow used to create a Pointer
    arrow = None
    startItem = None
    #
#    validPointerStart = [GSymbol, GCar, GCdr]
#    validPointerEnd = [GSymbol, GCons]

    def __init__(self, parent=None, *args, **kwargs):
        print parent
        self.xx = 0

        self.defaultMenu = QMenu("&GLisp")
        self.contextMenu = self.defaultMenu
        self.symbolMenu = QMenu("&Symbole")
        self.consMenu = QMenu("&Cons")
        GSymbol.contextMenu = self.symbolMenu
        GCons.contextMenu = self.consMenu

        super(GLisp, self).__init__(parent, *args, **kwargs)

        self.createActions()
        self.createMenus()
        self.createToolBar()

        self.parent = parent
# je crois que nil et t doivent être des variables globales

#        self.objectInserted.connect(self.objectInserted)

        self.mode = self.SelectOrMove
        self.arrow = None

    def repg(self, lisp):
        """Read, eval, print."""
        r = self.readLisp(lisp)
        p = self.printLisp(r)
        e = self.evalLisp(r)
        p += self.printLisp(e)
        return p

    def clear(self):
        for item in self.items():
            item.hide()

    def display(self, lisp):
        r = self.readLisp(lisp)
        self.displayObject(r)

    def evalAndDisplay(self, lisp):
        r = self.readLisp(lisp)
        e = self.evalLisp(r)
        self.displayObject(e)

    def displayObject(self, obj):
        """Print a lisp object."""
        if consp(obj):
            return self.displayList(obj)
        else:
            return self.displayAtom(obj)

    def displayAtom(self, obj):
        obj.show()

    def displayList(self, obj):
        if nilp(obj):
            return
        obj.show()
        self.displayObject(obj.getCar())
        self.displayList(obj.getCdr())

    def createActions(self):
        """Create all actions."""

        self.createSymbolAction = QAction(
            QIcon('icons/symbol.png'), u"Nouveau &Symbole",
            self, shortcut="Ctrl+S", statusTip=u"Ajouter un symbole",
            triggered=self.manualAddSymbol)

        self.createConsAction = QAction(
            QIcon('icons/cons.png'), u"Nouveau &Cons",
            self, shortcut="Ctrl+C", statusTip=u"Ajouter un cons",
            triggered=self.manualAddCons)

        self.deleteObjectAction = QAction(
            QIcon('icons/edit-delete.png'), u"Su&pprimer l'objet",
            self, shortcut="Ctrl+P", statusTip=u"Supprimer l'objet",
            triggered=self.deleteObject)

        self.editPnameAction = QAction(
            QIcon('icons/symbol.png'), u"Éditer Pna&me",
            self, shortcut="Ctrl+M", statusTip=u"Éditer le nom du symbole",
            triggered=self.editPname)

        self.selectCvalAction = QAction(
            QIcon('icons/pointer.png'), u"Sélectionner C&val …",
            self, shortcut="Ctrl+V", statusTip=u"Sélectionner la valeur",
            triggered=self.todo)

        self.nilCvalAction = QAction(
            QIcon('icons/symbol.png'), u"Cval = &nil",
            self, shortcut="Shift+N", statusTip=u"Mettre nil en Cval",
            triggered=self.todo)

        self.tCvalAction = QAction(
            QIcon('icons/symbol.png'), u"Cval = &t",
            self, shortcut="Shift+T", statusTip=u"Mettre t en Cval",
            triggered=self.todo)

        self.unsetCvalAction = QAction(
            QIcon('icons/symbol.png'), u"Cval N&ulle",
            self, shortcut="Ctrl+U", statusTip=u"Ne pas mettre de Cval",
            triggered=self.unsetCval)

        self.selectCarAction = QAction(
            QIcon('icons/pointer.png'), u"Sélectionner C&ar …",
            self, shortcut="Ctrl+A", statusTip=u"Sélectionner le Car",
            triggered=self.todo)

        self.nilCarAction = QAction(
            QIcon('icons/symbol.png'), u"Car = &nil",
            self, shortcut="Ctrl+N", statusTip=u"Mettre nil en Car",
            triggered=self.nilCar)

        self.tCarAction = QAction(
            QIcon('icons/symbol.png'), u"Car = &t",
            self, shortcut="Ctrl+T", statusTip=u"Mettre t en Car",
            triggered=self.todo)

        self.selectCdrAction = QAction(
            QIcon('icons/pointer.png'), u"Sélectionner C&dr …",
            self, shortcut="Ctrl+D", statusTip=u"Sélectionner le Cdr",
            triggered=self.todo)

        self.nilCdrAction = QAction(
            QIcon('icons/symbol.png'), u"Cdr = &nil",
            self, shortcut="Ctrl+Alt+N", statusTip=u"Mettre nil en Cdr",
            triggered=self.todo)

        self.tCdrAction = QAction(
            QIcon('icons/symbol.png'), u"Cdr = &t",
            self, shortcut="Ctrl+Alt+T", statusTip=u"Mettre t en Cdr",
            triggered=self.todo)

    def createMenus(self):
        """Create the menus."""

        self.defaultMenu.addAction(self.createSymbolAction)
        self.defaultMenu.setDefaultAction(self.createSymbolAction)
        self.defaultMenu.addAction(self.createConsAction)

        self.symbolMenu.addAction(self.editPnameAction)
        self.symbolMenu.setDefaultAction(self.editPnameAction)
        self.symbolMenu.addSeparator()
        self.symbolMenu.addAction(self.selectCvalAction)
        self.symbolMenu.addAction(self.nilCvalAction)
        self.symbolMenu.addAction(self.tCvalAction)
        self.symbolMenu.addAction(self.unsetCvalAction)
        self.symbolMenu.addSeparator()
        self.symbolMenu.addAction(self.deleteObjectAction)

        self.consMenu.addAction(self.selectCarAction)
        self.consMenu.setDefaultAction(self.selectCarAction)
        self.consMenu.addAction(self.nilCarAction)
        self.consMenu.addAction(self.tCarAction)
        self.consMenu.addSeparator()
        self.consMenu.addAction(self.selectCdrAction)
        self.consMenu.addAction(self.nilCdrAction)
        self.consMenu.addAction(self.tCdrAction)
        self.consMenu.addSeparator()
        self.consMenu.addAction(self.deleteObjectAction)

    def createToolBar(self):

        # The scene executes different actions on left click
        selectOrMoveButton = QToolButton()
        selectOrMoveButton.setCheckable(True)
        selectOrMoveButton.setChecked(True)
        selectOrMoveButton.setIcon(QIcon('icons/select.png'))
        addSymbolButton = QToolButton()
        addSymbolButton.setCheckable(True)
        addSymbolButton.setIcon(QIcon('icons/symbol.png'))
        addConsButton = QToolButton()
        addConsButton.setCheckable(True)
        addConsButton.setIcon(QIcon('icons/cons.png'))
        setPointerButton = QToolButton()
        setPointerButton.setCheckable(True)
        setPointerButton.setIcon(QIcon('icons/pointer.png'))

        # Tell the scene which of these exclusive modes to use
        self.mouseActionTypeGroup = QButtonGroup()
        self.mouseActionTypeGroup.addButton(selectOrMoveButton, self.SelectOrMove)
        self.mouseActionTypeGroup.addButton(addSymbolButton, self.AddSymbol)
        self.mouseActionTypeGroup.addButton(addConsButton, self.AddCons)
        self.mouseActionTypeGroup.addButton(setPointerButton, self.SetPointer)
        self.mouseActionTypeGroup.buttonClicked[int].connect(self.mouseActionGroupClicked)

        # Add all this in the one toolbar
        self.toolBar = QToolBar("GLisp")#self.parent.addToolBar("GLisp")
        self.toolBar.setMovable(False)
        self.toolBar.addAction(self.deleteObjectAction)
        self.toolBar.addWidget(selectOrMoveButton)
        self.toolBar.addWidget(addSymbolButton)
        self.toolBar.addWidget(addConsButton)
        self.toolBar.addWidget(setPointerButton)

    def mouseActionGroupClicked(self, i):
        # Set the mode corresponding with the clicked button
        self.mode = self.mouseActionTypeGroup.checkedId()

    def mousePressEvent(self, mouseEvent):
        # Here is what happens when we click on the scene

        # Right click on scene, 2 actions
        if mouseEvent.button() != Qt.LeftButton:
            self.rightClickPos = mouseEvent.scenePos()
            # Do nothing here if there's an item under the mouse
            if len(self.items(mouseEvent.scenePos())) != 0:
                return
            # In default mode, display the default context menu
            elif self.mode == self.SelectOrMove:
                self.clearSelection()
                self.defaultMenu.exec_(mouseEvent.screenPos())
            # Unselect all and go in default mode
            else:
                self.clearSelection()
                self.mode = self.SelectOrMove
                self.mouseActionTypeGroup.button(self.SelectOrMove).setChecked(True)
            return

        # Adding symbol
        if self.mode == self.AddSymbol:
            self.manualAddSymbol(mouseEvent.scenePos())

        # Adding cons
        elif self.mode == self.AddCons:
            self.manualAddCons(mouseEvent.scenePos())

        # Begin the creation of a Pointer
        elif self.mode == self.SetPointer and self.arrow == None:
            # Find
            startItems = self.items(mouseEvent.scenePos())

#editing
            while startItems:
                if isinstance(startItems[0], PointerAble):
                        self.startItem = startItems[0]
                        self.arrow = Arrow(self.startItem.scenePos() + self.startItem.pointerOffset,
                                           mouseEvent.scenePos())
                        self.addItem(self.arrow)
                        break
                if self.startItem != None:
                    break
                else:
                    startItems.pop(0)


        else:
            super(GLisp, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.mode == self.SetPointer and self.arrow:
            newLine = QLineF(self.arrow.line().p1(), mouseEvent.scenePos())
            self.arrow.setLine(newLine)
        elif self.mode == self.SelectOrMove:
            super(GLisp, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if self.mode == self.SetPointer and self.arrow:
            endItem = None
            endItems = self.items(self.arrow.line().p2())

            # We want the first valid item under the mouse pointer
            while endItems:
                if isinstance(endItems[0], ReferenceAble):
                    endItem = endItems[0]
                    self.startItem.setTarget(endItem)
#                    endItem.addReference(pointer)
#                    self.addItem(pointer)
                    break
                if endItem != None:
                    break
                else:
                    endItems.pop(0)


            # We've done with the temporary arrow
            self.removeItem(self.arrow)
            self.arrow = None
        super(GLisp, self).mouseReleaseEvent(mouseEvent)

    def deleteObject(self):
        for item in self.selectedItems():
            if not isinstance(item, GLispObject):
                return
            if isinstance(item, ReferenceAble):
                item.removeReferences()
            for child in item.childItems():
                if isinstance(item, PointerAble):
                    child.setTarget(None)
            self.removeItem(item)
#non paske faut clear le nom du symbol aussi…
    def addSymbol(self, name):
        pname = GString(name, None, self)
        symbol = GSymbol(pname, None, self)
        pname.setParentItem(symbol)
        self.symbols[name] = symbol
        return symbol

    def addCons(self, car, cdr):
        cons = GCons(car, cdr, None, self)
        # Do not remove this line unless you understand
        # why newly created Cons exists but are not drawn
        cons.scene()
        # /Do not remove
        return cons

    def manualAddSymbol(self, pos=None):
        if pos == None:
            pos = self.rightClickPos
        name = self.askValidSymbolName()
        if name:
            symbol = self.addSymbol(name)
            symbol.setPos(pos)

    def manualAddCons(self, pos=None):
        if pos == None:
            pos = self.rightClickPos
        cons = self.addCons(self.nil, self.nil)
        cons.setPos(pos)

    def askValidSymbolName(self, currentName=None):
        name, ok = QInputDialog.getText(None, "Symbole",
                "Nom du symbole (pname) :", QLineEdit.Normal,
                currentName)
        if ok and name != "" and name in self.symbols:
            q = QMessageBox(self.parent)
            q.setWindowTitle(u"Erreur lisp")
            q.setText(u"Un symbole avec ce nom existe.")
            q.setIconPixmap(QPixmap("icons/user-busy.png"))
            q.show()
        elif ok and name != "":
            return name
        return

    def selectClass(self):
        selected = None
        for item in self.selectedItems():
            if isinstance(item, selected):
                selected = item
                break
        return selected

    def editPname(self):
        symbol = selectClass(GSymbol)
        if not symbol:
            return
        name = self.askValidSymbolName(symbol.getPname().text)
        if not name:
            return
        del self.symbols[symbol.pname.text]
        self.removeItem(symbol.pname)
        pname = GString(name)
        symbol.pname = pname
        pname.setParentItem(symbol)
        self.symbols[name] = symbol

    def unsetCval(self):
        symbol = selectClass(GSymbol)
        if not symbol:
            return
        if not symbol:
            return
        # effacer la flèche sortante
        symbol.cval = None

    def nilCar(self):
        cons = self.selectClass(GCons)
        if cons == None:
            return
        cons.setCar(self.nil)

    # def reg(self, lisp):
    #     """Read, eval, print graphics."""
    #     r = self.readLisp(lisp)
    #     e = self.evalLisp(r)
    #     p = self.printGraphics(e)
    #     return p

    # def printGraphics(self, obj):
    #     return self.printObject(obj)

    def todo(self):
        QMessageBox.about(self.parent, "Todo",
                u"Cette fonctionnalité sera ajoutée prochaînement.")


class GLispWidget(QWidget, object):
    def __init__(self, parent=None, *args, **kwargs):
        super(GLispWidget, self).__init__(parent, *args, **kwargs)
        self.glisp = GLisp(self, *args, **kwargs)
        self.glisp.setSceneRect(QRectF(0, 0, 400, 300))
        self.view = QGraphicsView(self.glisp)
        self.view.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        layout = QHBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

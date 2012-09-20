#!/usr/bin/python
# -*- coding: utf-8 -*-

SPACE = " "
LPARENT = "("
RPARENT = ")"
DOT = "."
STRING = "\""
NPRIMF = 0
PRIMF = 1
TOOMUCHPARENT = 0
UNTERMINATEDLIST = 1
LACKINGCDR = 2
UNTERMINATEDCONS = 3
TOOMUCHINCDR = 4

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ParseError(Error):
    """Exception raised for errors."""
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class LispObject(object):
    """A common base for lisp objects."""
    def __init__(self, *args, **kwargs):
        super(LispObject, self).__init__(*args, **kwargs)

class Symbol(LispObject, object):
    """Symbol."""
    pname = None
    cval = None
    fval = None
    def __init__(self, pname, cval=None, fval=None, *args, **kwargs):
        super(Symbol, self).__init__(*args, **kwargs)
        self.setPname(pname)
        self.setCval(cval)
        self.setFval(fval)
    def setPname(self, pname):
        self.pname = pname
    def getPname(self):
        return self.pname
    def setCval(self, cval):
        self.cval = cval
    def getCval(self):
        return self.cval
    def setFval(self, fval):
        self.fval = fval
    def getFval(self):
        return self.fval

def symbolp(obj):
    """Symbol predicate."""
    return isinstance(obj, Symbol)

class Cons(LispObject, object):
    """Cons."""
    def __init__(self, car, cdr, *args, **kwargs):
        super(Cons, self).__init__(*args, **kwargs)
        self.setCar(car)
        self.setCdr(cdr)
    def getCar(self):
        return self.car
    def setCar(self, car):
        self.car = car
    def getCdr(self):
        return self.cdr
    def setCdr(self, cdr):
        self.cdr = cdr

def consp(obj):
    """Cons predicate."""
    #return type(obj) == Cons
    return isinstance(obj, Cons)

class Number(LispObject, object):
    """Number."""
    def __init__(self, number, *args, **kwargs):
        super(Number, self).__init__(*args, **kwargs)
        self.number = number

def numberp(obj):
    """Number predicate."""
    #return type(obj) == Number
    return isinstance(obj, Number)

class String(LispObject, object):
    """String."""
    def __init__(self, text, *args, **kwargs):
        super(String, self).__init__(*args, **kwargs)
        self.text = text

def stringp(obj):
    """String predicate."""
    #return type(obj) == String
    return isinstance(obj, String)

class Nil(Symbol, object):
    """Nil."""
    def __init__(self, *args, **kwargs):
        super(Nil, self).__init__(*args, **kwargs)

def nilp(obj):
    """Nil predicate."""
    #return type(obj) == Nil
    return isinstance(obj, Nil)

class T(Symbol, object):
    """True."""
    def __init__(self, *args, **kwargs):
        super(T, self).__init__(*args, **kwargs)

def tp(obj):
    """True predicate."""
    #return type(obj) == T
    return isinstance(obj, T)

def atomp(obj):
    return symbolp(obj) or stringp(obj) or numberp(obj)

def listp(obj):
    """List predicate."""
    return consp(obj) or nilp(obj)

class Primf(LispObject, object):
    """Primf."""
    def __init__(self, primitive, *args, **kwargs):
        super(Primf, self).__init__(*args, **kwargs)
        self.primitive = primitive

def primfp(obj):
    """Primf predicate."""
    #return type(obj) == Primf
    return isinstance(obj, Primf)

class Nprimf(LispObject, object):
    """Nprimf."""
    def __init__(self, primitive, *args, **kwargs):
        super(Nprimf, self).__init__(*args, **kwargs)
        self.primitive = primitive

def nprimfp(obj):
    """Nprimf predicate."""
    #return type(obj) == Nprimf
    return isinstance(obj, Nprimf)

class Lisp(object):
    """A lisp environment.

    A lisp environment.

    Args:
        debug: A bool toggling the print of debug messages.

    Returns:

    Raises:
        ParseError: An error occurred while reading a lisp expression.
    """

    nil = Nil(String("nil"))
    t = T(String("t"))

    def __init__(self, *args, **kwargs):
        super(Lisp, self).__init__(*args, **kwargs)
        print "fufufufufuf"
        self.symbols = {'nil': self.nil, 't': self.t}
        self.addPrimitive("quote", self.lispQuote, NPRIMF)
        self.addPrimitive("setq", self.lispSetq, NPRIMF)

    def rep(self, lisp):
        """Read, eval, print."""
        r = self.readLisp(lisp)
        e = self.evalLisp(r)
        p = self.printLisp(e)
        return p

    def red(self, lisp):
        """Read, eval, print dotted."""
        r = self.readLisp(lisp)
        e = self.evalLisp(r)
        p = self.printDotted(e)
        return p

    def lispQuote(self, obj):
        """nprimf
        (quote) => nil
        (quote . a) => nil
        (quote a) => a
        (quote (a b c)) => (a b c)
        (quote a b) => a
        """

        if not consp(obj):
            return self.nil
        return obj.getCar()

    def lispSetq(self, obj):
        """nprimf
        (setq c 1) => 1
        (setq c (quote (a b c d))) => (a b c d)
        """

        if not consp(obj):
            return self.nil
        if not symbolp(obj.getCar()):
            return self.nil
        if not consp(obj.getCdr()):
            return self.nil
        obj.getCar().setCval(self.evalLisp(obj.getCdr().getCar()))
        return obj.getCar().getCval()

    def findSymbol(self, name):
        if name in self.symbols:
            return self.symbols[name]
        return None

    def addSymbol(self, name):
        pname = String(name)
        symbol = Symbol(pname)
        self.symbols[name] = symbol
        return symbol

    def addPrimitive(self, name, primitive, ftype=NPRIMF):
        symbol = self.findSymbol(name)
        if (not symbol):
            symbol = self.addSymbol(name)
        if ftype == NPRIMF:
            primitive = Nprimf(primitive)
        elif ftype == PRIMF:
            primitive = Primf(primitive)
        else:
            return self.nil
        symbol.fval = primitive
        return symbol

    def addCons(self, car, cdr):
        return Cons(car, cdr)

    def printLisp(self, obj):
        return self.printObject(obj, False)

    def printDotted(self, obj):
        return self.printObject(obj, True)

    def printObject(self, obj, dotted=False):
        """Print a lisp object."""
        if consp(obj):
            return self.printList(obj, dotted)
        else:
            return self.printAtom(obj)

    def printAtom(self, obj):
        if symbolp(obj) or nilp(obj) or tp(obj):
            return obj.pname.text
        elif numberp(obj):
            return obj.number
        elif stringp(obj):
            return STRING + obj.text + STRING
        else:
            return ""

    def printList(self, obj, dotted=False, begin=True):
        p = ""

        if dotted:
            p = "("
            p += self.printObject(obj.getCar(), dotted)
            p += " . "
            p += self.printObject(obj.getCdr(), dotted)
            p += ")"
            return p

        if begin: # Starting list
            p += "("
            p += self.printObject(obj.getCar())
            p += self.printList(obj.getCdr(), dotted, False)
        elif (not listp(obj)): # List ends with a non nil atom
            p += " . "
            p += self.printAtom(obj)
            p += ")"
        elif (nilp(obj)): # List ends with nil
            p += ")"
        else: # Print the car and go to next cons
            p += " "
            p += self.printObject(obj.getCar())
            p += self.printList(obj.getCdr(), dotted, False)
        return p

    def evalLisp(self, obj):
        if consp(obj):
            return self.evalList(obj)
        elif symbolp(obj):
            return obj.getCval()
        else:
            return obj

    def evalList(self, obj):
        if not symbolp(obj.getCar()):
            return self.nil
        if not obj.getCar().fval:
            return self.nil
        if nprimfp(obj.getCar().fval):
            return obj.getCar().fval.primitive(obj.getCdr())
        if primfp(obj.getCar().fval):
            return obj.getCar().fval.primitive(self.evalNoFn(obj.getCdr()))
        return self.nil

    def evalNoFn(self, obj):
        if not consp(obj):
            return self.evalLisp(obj)
        return self.addCons(self.evalLisp(obj.getCar()), self.evalNoFn(obj.getCdr()))

    def readLisp(self, lisp=""):
        """Reads one or multiple lisp expressions.

        Reads one or multiple lisp expressions.

        Args:
            lisp: A string containing one or multiple lisp expressions.

        Returns:
            The lisp object corresponding to the expression,
            or in case of multiple expressions, the last expression.

        Raises:
            ParseError: An error occurred while reading a lisp expression.
        """

        read, lisp = self.readObject(lisp)
        lisp = lisp.lstrip(SPACE)
        if len(lisp) > 0:
            return self.readLisp(lisp)
        else:
            return read

    def readObject(self, lisp=""):
        lisp = lisp.lstrip(SPACE)
        if lisp[0] == RPARENT:
            raise ParseError(lisp, TOOMUCHPARENT)
        if lisp[0] == LPARENT:
            return self.readList(lisp[1:])
        return self.readAtom(lisp)

    def readList(self, lisp="", word1=True):
        lisp = lisp.lstrip(SPACE)
        if len(lisp) == 0:
            raise ParseError(lisp, UNTERMINATEDLIST)
        if lisp[0] == RPARENT: # End of list
            return self.nil, lisp[1:]
        if not word1 and lisp[0] == DOT: # Dot as cdr tag
            lisp = lisp[1:].lstrip(SPACE)
            if len(lisp) == 0:
                raise ParseError(lisp, LACKINGCDR)
            cdr, lisp = self.readObject(lisp)
            lisp = lisp.lstrip(SPACE)
            if len(lisp) == 0:
                raise ParseError(lisp, UNTERMINATEDCONS)
            if lisp[0] != RPARENT:
                raise ParseError(lisp, TOOMUCHINCDR)
            return cdr, lisp[1:]
        car, lisp = self.readObject(lisp)
        cdr, lisp = self.readList(lisp, False)
        return self.addCons(car, cdr), lisp

    def readAtom(self, lisp=""):
        word, lisp = self.readWord(lisp)
        if word.isdigit():
            return Number(word)
        if len(word) >= 2 and word[0] == STRING and word[-1] == STRING:
            return String(word[1:-1])
        if self.findSymbol(word):
            return self.findSymbol(word), lisp
        return self.addSymbol(word), lisp

    def readWord(self, lisp):
        index = 0
        while len(lisp) > index and lisp[index] not in [LPARENT, RPARENT, SPACE]:
            index += 1
        return lisp[:index], lisp[index:]

if __name__ == '__main__':
    lisp = Lisp()

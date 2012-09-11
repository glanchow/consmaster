#!/usr/bin/python
# -*- coding: utf-8 -*-

from lisp import *

class Solver(object):
    """Solver."""
    def __init__(self, *args, **kwargs):
        super(Solver, self).__init__(*args, **kwargs)

class listToDotted(Solver):
    """Convert a list to a dotted representation."""
    def __init__(self, question, *args, **kwargs):
        super(listToDotted, self).__init__(*args, **kwargs)
        lisp = Lisp()

        question = "(setq l (quote " + question + "))"
        print question
        self.question = lisp.rep(question)
        #print self.question
        self.answer = lisp.red("l")
        #print self.answer

    def test(self, answer):
        """Tests the user answer."""
        return answer == self.answer

if __name__ == '__main__':
    ex = listToDotted("(a b c)")
    print ex.question
    r = None
    while not r:
        a = raw_input()
        r = ex.test(a)
        print r
    # Answer is (a . (b . (c . nil)))

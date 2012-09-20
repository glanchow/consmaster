#!/usr/bin/python
# -*- coding: utf-8 -*-

from lisp import *
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.lisp = Lisp()

    def test_syntax(self):
        """Tests a variety of incorrect lisp expressions."""
        lisp = self.lisp
        for expr in [
            "(",
            "(()",
            ")",
            "())",
            ".)"
            ]:
            self.assertRaises(ParseError, lisp.readLisp, expr)

    def test_convert(self):
        """Tests the conversion between parenthesis and dotted notation."""
        paren = "(a (b c . d) (e) f)"
        dotted = "(a . ((b . (c . d)) . ((e . nil) . (f . nil))))"
        lisp = self.lisp
        self.assertEqual(dotted, lisp.printDotted(
            lisp.evalLisp(lisp.readLisp("(setq l (quote "+paren+"))"))))
        self.assertEqual(paren, lisp.printLisp(
            lisp.evalLisp(lisp.readLisp("(setq l (quote "+dotted+"))"))))

if __name__ == '__main__':
    unittest.main()

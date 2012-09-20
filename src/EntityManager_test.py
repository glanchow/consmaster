#!/usr/bin/python
# -*- coding: utf-8 -*-

from EntityManager import *
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_user(self):
        """Tests user list/add/del."""
        print
        print "Testing user list/add/del."
        print "User list = ", urep.findAll()
        print "Adding user"
        user = User("user_test", "password_test", "email_test")
        em.add(user)
        em.commit()
        print "User list = ", urep.findAll()
        print "Deleting user"
        em.delete(user)
        em.commit()
        print "user list = ", urep.findAll()
        print

    def test_exercice(self):
        """Tests exercice list/add/del."""
        print
        print "Testing exercice list/add/del."
        print "Exercice list = ", erep.findAll()
        print "Adding exercice"
        exercice = Exercice("(a b c)")
        em.add(exercice)
        em.commit()
        print "Exercice list = ", erep.findAll()
        print "Deleting exercice"
        em.delete(exercice)
        em.commit()
        print "Exercice list = ", erep.findAll()
        print

    def test_score(self):
        """Tests score list/add/del."""
        print
        print "Testing score list/add/del."
        print "Adding user, exercices, scores"
        user = User("testuser", "testpassword", "testemail")
        em.add(user)
        x1, x2, x3 = (
            Exercice("(a b c)"),
            Exercice("(a (b) c)"),
            Exercice("(a . (b . nil))")
        )
        em.add_all([x1, x2, x3])
        user.scores.append(Score(x1, timedelta(seconds=30)))
        user.scores.append(Score(x2, timedelta(seconds=40)))
        user.scores.append(Score(x3, timedelta(seconds=50)))
        em.commit()
        print "User scores list = ", user.scores
        print "Deleting exercices"
        em.delete(x1)
        em.delete(x2)
        em.delete(x3)
        em.commit()
        print "User scores list = ", user.scores
        print "Adding exercices, scores"
        x1, x2, x3 = (
            Exercice("(a b c)"),
            Exercice("(a (b) c)"),
            Exercice("(a . (b . nil))")
        )
        em.add_all([x1, x2, x3])
        user.scores.append(Score(x1, timedelta(seconds=30)))
        user.scores.append(Score(x2, timedelta(seconds=40)))
        user.scores.append(Score(x3, timedelta(seconds=50)))
        em.commit()
        print "User scores list = ", user.scores
        print "Exercice x1 scores list = ", x1.scores
        print "Deleting exercice x1"
        em.delete(x1)
        em.commit()
        print "User scores list = ", user.scores
        print "Deleting user, exercices, scores"
        em.delete(x2)
        em.delete(x3)
        em.delete(user)
        em.commit()
        print



if __name__ == '__main__':
    unittest.main()

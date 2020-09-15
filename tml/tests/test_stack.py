import unittest

from django.test import TestCase
from tml.utils import Stack



#./manage.py test tml.tests.test_stack
class TestStack(TestCase):
    def setUp(self):
        self.s = Stack()
        
    def test_push(self):
        self.s.push(3)

    def test_head(self):
        self.s.push(99)
        r = self.s.head()
        self.assertEqual(r, 99)
        
    def test_pop(self):
        self.s.push(77)
        r = self.s.pop()
        self.assertEqual(r, 77)        
        
    def test_isEmpty(self):
        self.assertTrue(self.s.isEmpty)
        
    def test_not_isEmpty(self):
        self.s.push(77)
        self.assertFalse(self.s.isEmpty)

    def test_length(self):
        self.s.push(55)
        self.s.push(77)
        self.s.push(99)
        self.assertEqual(self.s.length, 3)
        
    def test_multipush(self):
        self.s.push(555)
        self.s.push(777)
        self.s.push(999)
        r = self.s.pop()
        self.assertEqual(r, 999)
        r = self.s.pop()
        self.assertEqual(r, 777)
        r = self.s.pop()
        self.assertEqual(r, 555)

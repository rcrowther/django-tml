import unittest
from django.test import TestCase

from tml.parser import (
    InlineStartOrBlockMarkClosure, 
    ListElementOrCloseClosure,
    InlineStartSignal, 
    BlockMarkSignal,
    ListElementSignal,
    ListCloseSignal,
)



# ./manage.py test tml.tests.test_parser_closures
class TestParserClosures(TestCase):

    def test_class_match1(self):
        r = isinstance(InlineStartOrBlockMarkClosure, InlineStartSignal)
        self.assertTrue(r)

    def test_class_match2(self):
        r = isinstance(InlineStartOrBlockMarkClosure, BlockMarkSignal)
        self.assertTrue(r)

    def test_signal_class__match(self):
        r = isinstance(InlineStartOrNonListBlockClosure, ListElementSignal)
        self.assertFalse(r)
        
    def test_signal_class__match(self):
        r = isinstance(ListElementOrCloseClosure, ListCloseSignal)
        self.assertTrue(r)
        

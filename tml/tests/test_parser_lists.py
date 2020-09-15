import unittest

from django.test import TestCase
from tml.parser import Parser



# ./manage.py test tml.tests.test_parser_lists
class TestParserLists(TestCase):
    '''
    Base tests avoid reform creation, object deletion, subclassing
    '''
    def setUp(self):
        self.parser = Parser()
        
    def test_anon_list(self):
        b = []
        self.parser.feed(b, '- Lorem ipsum dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<ul><li><p>Lorem ipsum dolor</p></li></ul>')

    def test_anon_list_multi(self):
        b = []
        self.parser.feed(b, '- L')
        self.parser.feed(b, '- o')
        self.parser.feed(b, '- r')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<ul><li><p>L</p></li><li><p>o</p></li><li><p>r</p></li></ul>')
                        
    def test_anon_list_context(self):
        b = []
        self.parser.feed(b, 's')
        self.parser.feed(b, '- Lorem ipsum dolor')
        self.parser.feed(b, 'e')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>s</p><ul><li><p>Lorem ipsum dolor</p></li></ul><p>e</p>')
        
    def test_list(self):
        b = []
        self.parser.feed(b, '++')
        self.parser.feed(b, '-')
        self.parser.feed(b, 'Lorem ipsum dolor')
        self.parser.feed(b, '+')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<ul><li><p>Lorem ipsum dolor</p></li></ul>')

    def test_list_trailing_data(self):
        b = []
        self.parser.feed(b, '++')
        self.parser.feed(b, '- Lorem ipsum dolor')
        self.parser.feed(b, '+')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<ul><li><p>Lorem ipsum dolor</p></li></ul>')
        
    def test_list_ordered(self):
        b = []
        self.parser.feed(b, '+ol')
        self.parser.feed(b, '- Lorem ipsum dolor')
        self.parser.feed(b, '+')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<ol><li><p>Lorem ipsum dolor</p></li></ol>')

    def test_list_definition(self):
        b = []
        self.parser.feed(b, '+dl')
        self.parser.feed(b, '~ L')
        self.parser.feed(b, ': o')
        self.parser.feed(b, '+')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<dl><dt><p>L</p></dt><dd><p>o</p></dd></dl>')


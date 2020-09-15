import unittest

from django.test import TestCase
from tml.parser import Parser




# ./manage.py test tml.tests.test_parser
class TestParser(TestCase):
    '''
    Base tests avoid reform creation, object deletion, subclassing
    '''
    def setUp(self):
        self.parser = Parser()

    def test_feed(self):
        b = []
        self.parser.feed(b, 'Lorem ipsum dolor')
        #b = self.p.
        self.assertEqual(''.join(b), '<p>Lorem ipsum dolor')

    def test_line(self):
        b = []
        self.parser.feed(b, 'Lorem ipsum dolor')
        #b = self.p.
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem ipsum dolor</p>')

    def test_line_multi(self):
        b = []
        self.parser.feed(b, 'L')
        self.parser.feed(b, 'o')
        self.parser.feed(b, 'r')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>L o r</p>')

    def test_newline(self):
        b = []
        self.parser.feed(b, 'L')
        self.parser.feed(b, '')
        self.parser.feed(b, 'o')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>L</p><p>o</p>')

    def test_newline_multi(self):
        b = []
        self.parser.feed(b, 'L')
        self.parser.feed(b, '')
        self.parser.feed(b, '')
        self.parser.feed(b, '')
        self.parser.feed(b, 'o')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>L</p><p>o</p>')
                
    def test_inline(self):
        b = []
        self.parser.feed(b, 'Lorem [   ipsum] dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem <span>ipsum</span> dolor</p>')

    def test_inline_tagname(self):
        b = []
        self.parser.feed(b, 'Lorem [cite   ipsum] dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem <cite>ipsum</cite> dolor</p>')

    def test_inline_anchor(self):
        b = []
        self.parser.feed(b, 'Lorem [a(https://lipsum.com/) ipsum] dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem <a href="https://lipsum.com/">ipsum</a> dolor</p>')
        
    def test_inline_nest(self):
        b = []
        self.parser.feed(b, '[cite Lorem [i ipsum] dolor]')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p><cite>Lorem <i>ipsum</i> dolor</cite></p>')
                        
    def test_headline(self):
        b = []
        self.parser.feed(b, '==== Lorem')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<h4>Lorem</h4>')
        
    # def test_tabarea(self):
        # b = []
        # self.parser.feed(b, '    Lorem ipsum dolor')
        # self.parser.close(b)
        # self.assertEqual(''.join(b), '<pre><code>Lorem ipsum dolor\n</code></pre>')

    # def test_tabarea_multi(self):
        # b = []
        # self.parser.feed(b, '    Lorem')
        # self.parser.feed(b, '      ipsum')
        # self.parser.feed(b, '     dolor')
        # self.parser.close(b)
        # self.assertEqual(''.join(b), '<pre><code>Lorem\n  ipsum\n dolor\n</code></pre>')

    # def test_tabarea_context(self):
        # b = []
        # self.parser.feed(b, 's')
        # self.parser.feed(b, '    Lorem ipsum dolor')
        # self.parser.feed(b, 'e')
        # self.parser.close(b)
        # self.assertEqual(''.join(b), '<p>s</p><pre><code>Lorem ipsum dolor\n</code></pre><p>e</p>')

    def test_escape(self):
        b = []
        self.parser.feed(b, '??')
        self.parser.feed(b, '    Lorem')
        self.parser.feed(b, '?')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<pre>    Lorem\n</pre>')

    def test_escape_multi(self):
        b = []
        self.parser.feed(b, '??')
        self.parser.feed(b, '   L')
        self.parser.feed(b, ' o')
        self.parser.feed(b, '  r')
        self.parser.feed(b, '?')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<pre>   L\n o\n  r\n</pre>')

    def test_escape_context(self):
        b = []
        self.parser.feed(b, 's')
        self.parser.feed(b, '??')
        self.parser.feed(b, '    Lorem')
        self.parser.feed(b, '?')
        self.parser.feed(b, 'e')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>s</p><pre>    Lorem\n</pre><p>e</p>')
        
    def test_blockquote(self):
        b = []
        self.parser.feed(b, '>>')
        self.parser.feed(b, 'Lorem ipsum dolor')
        self.parser.feed(b, '>')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<blockquote><p>Lorem ipsum dolor</p></blockquote>')

    def test_blockquote(self):
        b = []
        self.parser.feed(b, '>>')
        self.parser.feed(b, 'Lorem ipsum dolor')
        #self.parser.feed(b, 'sit amet,')
        #self.parser.feed(b, 'consectetur adipiscing elit.')
        self.parser.feed(b, '>')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<blockquote><p>Lorem ipsum dolor</p></blockquote>')

    def test_blockquote_multi(self):
        b = []
        self.parser.feed(b, '>>')
        self.parser.feed(b, 'L')
        self.parser.feed(b, 'o')
        self.parser.feed(b, 'r')
        self.parser.feed(b, '>')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<blockquote><p>L o r</p></blockquote>')
        

    # def test_blockquote(self):
        # b = []
        # self.parser.feed(b, '>>')
        # self.parser.feed(b, 'Lorem ipsum dolor')
        # #self.parser.feed(b, 'sit amet,')
        # #self.parser.feed(b, 'consectetur adipiscing elit.')
        # self.parser.feed(b, '>')
        # self.parser.close(b)
        # self.assertEqual(''.join(b), '<blockquote><p>Lorem ipsum dolor</p></blockquote>')

    # def test_blockquote_multi(self):
        # b = []
        # self.parser.feed(b, '>>')
        # self.parser.feed(b, 'L')
        # self.parser.feed(b, 'o')
        # self.parser.feed(b, 'r')
        # self.parser.feed(b, '>')
        # self.parser.close(b)
        # self.assertEqual(''.join(b), '<blockquote><p>Lor</p></blockquote>')

import unittest

from django.test import TestCase
from tml.parser import Parser, ParseError




# ./manage.py test tml.tests.test_parser
class TestParserLineHandling(TestCase):
    '''
    Test that handles lines and paragraphing
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


class TestParserInlineCodes(TestCase):
    '''
    Test that output is as expected from imput codes
    '''
    def setUp(self):
        self.parser = Parser()
                
    def test_inline(self):
        b = []
        self.parser.feed(b, 'Lorem { ipsum} dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem <span>ipsum</span> dolor</p>')

    def test_inline_tagname(self):
        b = []
        self.parser.feed(b, 'Lorem {cite   ipsum} dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem <cite>ipsum</cite> dolor</p>')

    def test_inline_classname(self):
        b = []
        self.parser.feed(b, 'Lorem {span.price   ipsum} dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem <span class="price">ipsum</span> dolor</p>')

    def test_inline_nest(self):
        b = []
        self.parser.feed(b, '{cite Lorem {i ipsum} dolor}')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p><cite>Lorem <i>ipsum</i> dolor</cite></p>')


class TestParserAnchorCodes(TestCase):
    '''
    Test that output is as expected from imput codes
    Anchoirs have some special handling
    '''
    def setUp(self):
        self.parser = Parser()
        
    def test_inline_anchor(self):
        b = []
        self.parser.feed(b, 'Lorem {a(https://lipsum.com/) ipsum} dolor')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>Lorem <a href="https://lipsum.com/">ipsum</a> dolor</p>')

    def test_inline_anchor_default(self):
        b = []
        self.parser.feed(b, '{a() ipsum}')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p><a href="#">ipsum</a></p>')
        
    def test_inline_anchor_autowrite(self):
        b = []
        self.parser.feed(b, '{a(https://lipsum.com/)}')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p><a href="https://lipsum.com/">https://lipsum.com/</a></p>')
              
              
class TestParserStructuralCodes(TestCase):
    '''
    Test that output is as expected from imput codes
    '''
    def setUp(self):
        self.parser = Parser()
                                
    def test_headline(self):
        b = []
        self.parser.feed(b, '==== Lorem')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<h4>Lorem</h4>')

    def test_image(self):
        b = []
        self.parser.feed(b, '*(Lorem)')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<figure><img src="Lorem" alt="image of Lorem"/></figure>')        

    def test_all_image(self):
        b = []
        self.parser.feed(b, '*.big(Lorem)"ipsum"')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<figure><img src="Lorem" alt="image of Lorem" class="big"/><figcaption>ipsum</figcaption></figure>')        
                
        
    def test_block(self):
        b = []
        self.parser.feed(b, '##')
        self.parser.feed(b, 'Lorem ipsum dolor')
        self.parser.feed(b, '#')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<div><p>Lorem ipsum dolor</p></div>')

    def test_block_tagname(self):
        b = []
        self.parser.feed(b, '#article')
        self.parser.feed(b, 'Lorem ipsum dolor')
        self.parser.feed(b, '#')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<article><p>Lorem ipsum dolor</p></article>')

    def test_block_classname(self):
        b = []
        self.parser.feed(b, '##.warning')
        self.parser.feed(b, 'Lorem ipsum dolor')
        self.parser.feed(b, '#')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<div class="warning"><p>Lorem ipsum dolor</p></div>')
        
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

    def test_escape_tml(self):
        b = []
        self.parser.feed(b, 's')
        self.parser.feed(b, '??')
        self.parser.feed(b, '#feelgood')
        self.parser.feed(b, '?')
        self.parser.feed(b, 'e')
        self.parser.close(b)
        self.assertEqual(''.join(b), '<p>s</p><pre>#feelgood\n</pre><p>e</p>')

    def test_escape_multiopen_thows_error(self):
        b = []
        with self.assertRaises(ParseError):
            self.parser.feed(b, 's')
            self.parser.feed(b, '??')
            self.parser.feed(b, '?pre')
            self.parser.feed(b, '?')
            self.parser.feed(b, 'e')
            self.parser.close(b)

    def test_escape_unopened_close_throws_error(self):
        b = []
        with self.assertRaises(ParseError):
            self.parser.feed(b, 's')
            self.parser.feed(b, '##')
            self.parser.feed(b, '    Lorem')
            self.parser.feed(b, '?')
            self.parser.feed(b, 'e')
            self.parser.close(b)        
                        
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

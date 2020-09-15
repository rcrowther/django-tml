import unittest

from django.test import TestCase
from tml.parser import CodeBlockParser, PrismParser




# ./manage.py test tml.tests.test_parser_subclass
class TestSubclass(TestCase):
    '''
    Base tests avoid reform creation, object deletion, subclassing
    '''
    def test_codeblock(self):
        p = CodeBlockParser()
        b = []
        p.feed(b, '??')
        p.feed(b, 'Lorem')
        p.feed(b, '?')
        self.assertEqual(''.join(b), '<figure><pre><code contenteditable spellcheck="false">Lorem\n</code></pre></figure>')

    def test_prism(self):
        p = PrismParser()
        b = []
        p.feed(b, '?ada')
        p.feed(b, 'Lorem')
        p.feed(b, '?')
        self.assertEqual(''.join(b), '<figure><pre><code contenteditable spellcheck="false" class="language-ada">Lorem\n</code></pre></figure>')

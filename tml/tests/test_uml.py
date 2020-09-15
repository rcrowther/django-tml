import unittest

from django.test import TestCase
from tml import uml



# ./manage.py test tml.tests.test_uml
class TestUML(TestCase):

    # Theres a lot to UML. Test only the smartquotes work.
    
    def test_dquote_open(self):
        self.assertEqual("\u201C", uml.all('""'))

    def test_dquote_close(self):
        self.assertEqual("\u201D", uml.all('"'))
        
    def test_quote_open(self):
        self.assertEqual("\u2018", uml.all("''"))

    def test_quote_close(self):
        self.assertEqual("\u2019", uml.all("'"))

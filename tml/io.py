import io
from tml.parser import Parser
from django.utils.html import mark_safe



def html(value, parser=Parser, uml=False):
    '''
    Convert any TML to html.
    '''
    # The Parser is a feed parser, it does not take a source, it accepts
    # a feed of lines, and needs a builder for output. The lines must be
    # in a particular form, stripped of trailing newlines. This can be 
    # done using a io.StringIO object, which can normalise the lineends
    # then feed them in chunks.
    b = []

    # stringIO returning single '\n'
    s = io.StringIO(value, newline=None)
    parser = parser(uml=uml)
    for line in s:
        parser.feed(b, line.rstrip())
    parser.close(b)
    return mark_safe(''.join(b))

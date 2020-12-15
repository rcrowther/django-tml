# popups
#https://duckduckgo.com/?q=javascript+popup+overlay&t=lm&ia=web
#https://daringfireball.net/projects/markdown/syntax
#https://www.webdesign.org/web-programming/javascript/creating-a-floating-window.10895.html
#https://uk.answers.yahoo.com/question/index?qid=20110306114320AAUYJE8

text= (
"GENERAL TEXT\n"
"   • Two or more newlines are reduced to a paragraph start/stop\n"
"   • All other whitespace reduced to one space\n"
"BLOCK-LEVEL (place hard left)\n"
"   = headline\n"
"   ==== headline (four-deep)\n"
"   ++\n"
"   - list item\n"
"   +\n\n"
"   +ol\n"
"   - ordered list item\n"
"   +\n\n"
"   +dl\n"
"   ~ term\n"
"   : definition\n"
"   +\n\n"
"   >>\n"
"       blockquote\n"
"   >\n\n"
#"   **{image-address} image caption*\n\n"
"   ??\n"
"       unformatted\n"
"   ?\n\n"
"INLINE-LEVEL (in text)\n"
"   {a(link address) link text}\n"
)

html = (
"<h3>General Text</h3>"
"<p>Two or more newlines are reduced to a paragraph start/stop</p>"
"<p>All other whitespace reduced to one space</p>"
"<h3>Block-level (hard left)</h3>"
"<h4>Attributes</h4>"
"<i>mark</i>HTMLtag,class(href)\"text\""
"<h4>Marks</h4>"
"<pre><code>"
"= headline\n"
"==== headline (four-deep)\n"
"++\n"
"- list item\n"
"+\n"
"+dl\n"
"~ term\n"
": definition\n"
"+\n"
">>\n"
"    blockquote\n"
">\n"
"*(image-address)\"image caption\*\n"
"??\n"
"    escaped\n"
"?\n"
"</code></pre>"
"<h3>Inline-level (in text)</h3>"
"<pre><code>"
"{a(link address) link text}\n"
"</code></pre>"
)

helpicon = (
'<svg height="24" width="24">'
  '<defs>'
    '<filter id="shadow" x="0" y="0" width="200%" height="200%">'
      '<feGaussianBlur stdDeviation="1 1" result="shadow"/>'
      '<feOffset dx="1" dy="1" />'
    '</filter>'
  '</defs>'
  '<circle cx="12" cy="12" r="10" style="stroke:#e6e6ff; stroke-width:4; fill:#aaaaff"/>'
  '<text style="filter: url(#shadow); fill: #000" x="9" y="17">?</text>'
  '<text fill="#fff" font-size="14" font-family="sans" x="9" y="17">?</text>'
  'Sorry, your browser does not support inline SVG.'
'</svg>'
)

from django.utils.safestring import mark_safe
 

    #b.append('<div id="tml-help-button" style="margin-left:160px">')
    #b.append('<span id="tml-help-button">')

def helpbutton(as_span=False):
    b = []
    if (as_span):
        b.append('<span id="tml-help-button">')
    else:
        b.append('<div id="tml-help-button">')
    b.append('<a href="#tml-display" class="button">')
    b.append(helpicon)
    b.append('(markup)')
    b.append('</a>')
    b.append('<div id="tml-display">')
    b.append('<div class="toolbar">')
    b.append('<span class="cancel">')
    b.append('<a href="#">&times;</a>') 
    b.append('</span>')
    b.append('</div>')
    b.append(html)
    b.append('</div>')
    if (as_span):
        b.append('</span>')
    else:
        b.append('</div>')
    #b.append('<div id="tml-overlay" class="overlay"></div>')
    return mark_safe(''.join(b))



from django.forms.widgets import Textarea


# use tml initially?
# position top/left
#? At top not working because will not go over label?
#! extra spacing CSS, if not button
#? offer button option
class TMLTextarea(Textarea):
    template_name = 'tml/forms/widgets/textarea.html'
    
    
    def __init__(self, attrs=None, help_at_right=True):
        super().__init__(attrs)
        self.help_at_right = help_at_right

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx['widget']['tmlhelp'] = helpbutton(self.help_at_right)
        return ctx
        
    class Media:
        css = {
            'all': ('tml/css/help.css',)
        }

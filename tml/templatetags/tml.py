from django import template
from django.template.defaultfilters import stringfilter
#from django.utils.html import mark_safe
from tml import uml as uml_module
from tml import html
from tml.parser import PrismParser

register = template.Library()


@register.filter()
@stringfilter
def tml(value):
    return html(value)
        
@register.filter()
@stringfilter
def uml(value):
    return uml_module.all(value)
    
@register.filter()
@stringfilter
def tml_uml(value):
    return html(value, uml=True)

@register.filter()
@stringfilter
def tml_uml_prism(value):
    return html(value, parser=PrismParser, uml=True)

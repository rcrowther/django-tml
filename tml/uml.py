import re


# Markup for creating inaccessible unicode codepoints.
#
# This is an easy-to-understand way of creating common
# codepoints, mostly using keyboard-available characters. Like any 
# conversion methods for typography, these methods will
# make mistakes. The hope is only that the improvement outweighs
# mistakes.
#
# Legal marks,
# "(c)" = copyright
# "(t)" = trademark
# "(r)" = registered
#
# Hyphens, dashes,
# "---" = em for new material, or sentence joining.
# "--" = en for ranges.
# "-." = dictionary hyphen.
# "-" = hyphen.
#
# Ellipse,
# "..." = ellipsis for missiung text, including tailing off.
#
# Quotes,
# "''" single quotes open
# "'" single quote close, and apostrophe
# "\"\""  double quote open 
# "\"" double quote close
# "<<" guillemet open
# ">>" guillemet close
#
# Mathematical multiply/minus, and degree.
# ":mx" = multiply
# ":m-" = minus
# ":mo" = degree
#
def orCat(*args):
    return '|'.join(args)

def nonCapture(stringpattern):
    return "(?:" + stringpattern + ')'

def group(stringpattern):
    return '(' + stringpattern + ')'    
    
    
doubleQuoteSP = r'""?'
singleQuoteSP = r"''?"
guillemetOpenSP = r"<<"

#NB the 'not newline' is here because it clashes with TML blockquote 
# open. This assumes UML runs before TML (or anything else), but 
# harmless if not.
guillemetCloseSP = r">>"
quoteSP = orCat(
    singleQuoteSP, 
    doubleQuoteSP, 
    guillemetOpenSP,
    guillemetCloseSP
    )
quoteP = re.compile(quoteSP, re.UNICODE)
quoteMap = {
    "'":"\u2019",
    "''":"\u2018",
    '"':"\u201D",
    '""':"\u201C",
    '<<':"\u00AB",
    '>>':"\u00BB"
}

def quoteCB(mo):
    return quoteMap[mo.group()]

def quote(string):
    return re.sub(quoteP, quoteCB, string)
  


elipsisSP = nonCapture(r"\.\.\.")
hyphenDashSP = nonCapture(r"-(?:-{1,2}|\.)?")
legalMarkSP = nonCapture(r"\([ctr]\)")
punctuationSP = orCat(
    elipsisSP, 
    hyphenDashSP, 
    legalMarkSP
    )
punctuationP = re.compile(punctuationSP, re.UNICODE)
punctuationMap = {
    '-':"\u2010",
    '-.':"\u2027",
    '--':"\u2013",
    '---':"\u2014",
    '...':"\u2026",
    '(c)':"\u00A9",
    '(t)':"\u2122",
    '(r)':"\u00AE"
}

def punctuationCB(mo):
    return punctuationMap[mo.group()]

def punctuation(string):
    return re.sub(punctuationP, punctuationCB, string)


scisymSP = r":m[xo-]" 
scisymP = re.compile(scisymSP, re.UNICODE)
scisymMap = {
    ':mx':"\u00D7",
    ':m-':"\u2212",
    ':mo':"\u00B0"
}

def scisymCB(mo):
    return scisymMap[mo.group()]

def scisym(string):
    return re.sub(scisymP, scisymCB, string)
  
  
allSP = orCat(quoteSP, punctuationSP, scisymSP)  
allP = re.compile(allSP, re.UNICODE)
allMap = dict(**quoteMap)
allMap.update(punctuationMap)
allMap.update(scisymMap)

def allCB(mo):
    return allMap[mo.group()]
    
def all(string):
    return re.sub(allP, allCB, string)

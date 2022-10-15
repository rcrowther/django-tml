from tml.utils import Stack
from tml import uml
from django.utils.html import conditional_escape
from collections import namedtuple
import pathlib

Mark = namedtuple('Mark', ['tagname', 'idName', 'classname', 'href', 'text'])



class ParseError(Exception):
    def __init__(self, lineno, message, data=''):
        # data is, for example, the line text, or stored matches etc.
        if data:
            data = '\n    ' + data        
        fullMessage = "src:{} {}{}".format(lineno, message, data)
        super().__init__(fullMessage)


                        
class CloseType():
    '''
    Type of closure for vlocks.
    Seems complex, but makes sense to humans.
    '''
    #def __init__(closeType=None) 
    #    self.closeType = closeType
    def __repr__(self):
        return self.__class__.__name__
        
# headlines, anonyomous list elements
#x
# class NotStacked(CloseType):
    # pass
#NotStackedClosure = LineEndSignal()

# bracketted blocks
#NB The signal is never used. IT's a placeholder for the 
# MarkData atttribute.
class TargetedMarkSignal(CloseType):
    pass
TargetedMarkClosure = TargetedMarkSignal()

# list
class ListElementSignal(CloseType):
    pass
#ListMarkClosure = ListMarkSignal()

# list element
class ListCloseSignal(CloseType):
    pass
    
# used for closing selfclosing list blocks
class ListElementOrCloseReciever(
    ListElementSignal, 
    ListCloseSignal
):
    pass
ListElementOrCloseClosure = ListElementOrCloseReciever()



# parse content e.g. paragraphs, partially
class BlockMarkSignal(CloseType):
    pass
#BlockMarkClosure = BlockMark()

# parse content e.g. paragraphs, partially
class InlineStartSignal(CloseType):
    pass
#ParseContentStartClosure = BlockMark()
    
# tabbed area and paragraph
class InlineStartOrBlockMarkReciever(
    InlineStartSignal, 
    BlockMarkSignal,
    ListElementSignal,
    ListCloseSignal,
):
    pass
InlineStartOrBlockMarkClosure = InlineStartOrBlockMarkReciever()

#anonyomous list block,
class InlineStartOrNonListBlockReciever(
    InlineStartSignal, 
    BlockMarkSignal,
):
    pass
InlineStartOrNonListBlockClosure = InlineStartOrNonListBlockReciever()


# Inline
class InlineCloseMark():
    pass
InlineCloseMarkOrLineEndClosure = InlineCloseMark()
    

        
class MarkData():
    '''
    Carries markdata, with formatting, error and error anticipation 
    data
    
    mark
        a parsed representation of a mark
    control
        the text mark which triggered creating this class
    '''
    #? The mix of error and formatting data is not good 
    def __init__(self, mark, closeType, control, open_lineno=None):
        self.mark = mark 
        self.closeType = closeType
        self.control = control 
        
        # Linenumber of opening mark. For errors in explicit close marks
        self.open_lineno = open_lineno
        
    def open(self, b):
        b.append('<')
        b.append(self.mark.tagname)
        if (self.mark.idName):
            b.append(' id="')
            b.append(self.mark.idName)
            b.append('"')
        if (self.mark.classname):
            b.append(' class="')
            b.append(self.mark.classname)
            b.append('"')
        b.append('>')
        #if (self.mark.classname):
        #    b.append('<{} class="{}">'.format(self.mark.tagname, self.mark.classname))
        #else:
        #    b.append('<{}>'.format(self.mark.tagname))

    def close(self, b):
        b.append('</{}>'.format(self.mark.tagname))
        
    def error_str(self):
        return "control '{}' opened at line:{}".format(self.control, self.open_lineno)

    def __repr__(self):
        return "MarkData(mark='{}', closeType={}, control='{}', open_lineno={})".format(
            self.mark,
            self.closeType,
            self.control, 
            self.open_lineno,
        )        
        
#?        
class ParagraphMarkData(MarkData):
    def __init__(self, **kwargs):
        super().__init__(Mark('p', '', '', '', ''), InlineStartOrBlockMarkClosure, '\\n', **kwargs)



class AnchorMarkData(MarkData):
    # This hold now?
    def __init__(self, mark, open_lineno=None):
        super().__init__(mark, TargetedMarkClosure, '{', open_lineno)
    
    # tagname is on mark?
    def open(self, b):
        href =  '#'   
        if (self.mark.href):
            href = self.mark.href
        if (self.mark.classname):
            b.append('<a href="{}" class="{}">'.format(href, self.mark.classname))
        else:
            b.append('<a href="{}">'.format(href))

    
    
#? figure something better, surely
class PreMarkData(MarkData):
    def __init__(self, mark, open_lineno=None):
        super().__init__(mark, TargetedMarkClosure, '?', open_lineno)

    # def open(self, b):
        # if (self.mark.classname):
            # b.append('<pre class="{}">'.format(self.mark.classname))
        # else:
            # b.append('<pre>')
            
    # def close(self, b):
        # b.append('</pre>')  



class Parser:
    '''
    Line based feed parser.
    
    Needs to supply a builder and feed lines to it. Needs close() 
    calling on it.
    
    uml
        call UML on parsed items. It will skip block controls and 
        escaped lines. However, current implementation is a little 
        crude, it will apply regexes to inline codes. Worst scenario is 
        it damages URLs which parameter anchor tags.
    '''
    Newline = '\n'
    Tab = '\t'
        
    BlockBracketMarks = ['#', '+', '>']
    BlockListElementMarks = ['-', '~', ':']
    BlockTitleMark = '='
    InlineOpenMark = '{'
    InlineCloseMark = '}'
    
    BlockSignificantMarks = ( 
        BlockBracketMarks
        )

    # overridable attribute for markdata class
    pre_markdata = PreMarkData

    shortcutBlockTags = {
          '#' : 'div', 
          '+' : 'ul', 
          '?' : 'pre',
          '>' : 'blockquote',
          '{' : 'span',
    }

    #NB Not rendered through stack, or with attributes, so needs no 
    # MarkData
    listElementTags = { 
      '-': 'li',
      '~': 'dt',
      ':': 'dd',
    }
        

    def __init__(self, uml=False):
        self.inlineB = []
        self.reset(uml=uml)

    def reset(self, uml=False):
        self.uml = uml
        self.lineno = 0
        self.line = ''
        self.linepos = 0
        self.linelen = 0
        self.closeStack = Stack()
        self.inPara = False
        self.inEscape = False
    
    
    # text handling
    
    def isWhitespace(self, c):
        return (ord(c) < 33)
        
    def countIndent(self):
        i = 0
        while (self.isWhitespace(self.line[i]) and i < self.linelen):
            i += 1
        return i
        
        
        
    # Line reading
                
    def cpGet(self):
        '''
        Get a copdepoint from the stored line.
        A quiet function that throws no errors
        Increments the lineposition.
        return
            A codepoint. if at lineend, None
        '''
        r = None
        if (self.linepos < self.linelen):
            r = self.line[self.linepos]
            self.linepos += 1
        return r

    def cpPeek(self):
        '''
        Get a copdepoint from the stored line.
        A quiet function that throws no errors
        Will not move the lineposition.
        return
            A codepoint. if at lineend, None
        '''
        r = None
        if (self.linepos < self.linelen):
            r = self.line[self.linepos]
        return r
                
    def cpSkip(self):
        self.linepos += 1
                            
    # needs to be defensive to get a tagname
    def getUntilWhiteSpace(self):
        '''
        Eat input from current pos until whitespace.
        Note this is a tricky function. It eats the limiting 
        whitespace. It also will not error, returning as much as it can
        find, and quietly stopping at lineends.
        '''
        b = []
        c = self.cpGet()
        while (c and not self.isWhitespace(c)):
            b.append(c)
            c = self.cpGet()
        return ''.join(b)
                
    def skipWhiteSpace(self):
        '''
        Cross whitespace.
        Starts at current position. If whitespace, move forward
        until either not whitespace, or input exhausted.
        
        return
            The peeked non whitespace char. if EOL, None
        '''
        c = self.cpPeek()
        while(c and self.isWhitespace(c)):
            self.linepos += 1
            c = self.cpPeek()
        return c



    def parseAttributes(self, cntrlChar):
        '''
        Parse attributes inside a markup tag
        Starts after the control.
        Ends beyond delimiter, either whitespace, linend or ')'
        This is a quiet function.
        '''
        tagnameB = []
        tagB = []
        tag = ''
        idB = []
        classB = []
        tagclassnameB = []
        hrefB = []
        textB = []
        
        c = self.cpGet()
        
        # tagname
        if (c == cntrlChar):
            tag = self.shortcutBlockTags.get(c, None)
            
            # move on
            c = self.cpGet()
        else:
            while (c and not self.isWhitespace(c) and c != '#' and c != '.' and c != '(' and c != '"'):
                tagB.append(c)
                c = self.cpGet()
            tag = ''.join(tagB)
            
        # Check there is a tagName
        if (not tag):
            raise ParseError(
                self.lineno, 
                "No tag parsed in attributes", 
                self.line
            )
            
        # identity
        if (c == '#'):
            c = self.cpGet()
            while (c and not self.isWhitespace(c) and c != '.' and c != '(' and c != '"'):
                idB.append(c)
                c = self.cpGet()                     
                    
        # class
        if (c == '.'):
            c = self.cpGet()
            while (c and not self.isWhitespace(c) and c != '(' and c != '"'):
                classB.append(c)
                c = self.cpGet() 
                                    
        # while (c and not self.isWhitespace(c) and c != '(' and c != '"'):
            # tagclassnameB.append(c)
            # c = self.cpGet()
            
        # now get tag and class names
        # tagclassname =  ''.join(tagclassnameB) 
        # splitC = tagclassname.split('.', 1)
        # tagname = splitC[0]
        # classname = ''
        # if (len(splitC) > 1):
            # classname = splitC[1] 
 
        # Now parse href
        if (c == '('):
            c = self.cpGet()
            while (c and (c != ')')):
                hrefB.append(c)            
                c = self.cpGet() 

        # ...now text
        if (self.cpPeek() == '"'):
            self.cpSkip()
            c = self.cpGet()
            while (c and (c != '"')):
                textB.append(c)            
                c = self.cpGet()                 
        return Mark(tag, ''.join(idB), ''.join(classB), ''.join(hrefB), ''.join(textB))
        #return Mark(tagname, classname, ''.join(hrefB), ''.join(textB))


    # Block stack handling
              
    def expectedHeadPopClose(self, b, control):
        '''
        Pop and render data from the closeStack head.
        Used for closes that are marked, such as blockquote blocks.
        '''
        e = self.closeStack.pop()
        if (e is None or e.control != control):
            found = 'StackEmpty' if (e is None) else e.control
            raise ParseError(
                self.lineno, 
                "Expected different mark. mark:'{}', found:{}".format(control, found), 
                ''
            )
        else:
            e.close(b)

    def typeMatchPopClose(self, b, tpe):
        '''
        Pop and render data from the closeStack with given type.
        tpe
            A class of closure type e.g. InlineStartOrBlockMarkReciever
        '''
        #NB word of explaination: all type match pops() are at a block 
        # level, not inline. All signals assume paragraph closure 
        # except InlineStartSignal, which is sent after paragraphs are
        # closed. So it is currently ok to kill this essentially
        # cached attribute here.
        self.inPara = False

        # empty stack of all marks that close on block starts
        e = self.closeStack.head()
        while (e and isinstance(e.closeType, tpe)):
            m = self.closeStack.pop()
            m.close(b)
            e = self.closeStack.head()
        
    def markOpenPush(self, b, markData):
        '''
        Render and push data to the closeStack. 
        '''
        # write the open tag
        markData.open(b)
        
        # push the closeMark
        self.closeStack.push(markData)
        
                
    # inline
        
    def onInlineOpen(self, b, cntrlChar):
        '''
        Start is the control cp
        end is past the delimiter, first non-whitespace or line-end.
        '''
        mark = self.parseAttributes(cntrlChar)     
        if (mark.tagname == 'a'):
            d = AnchorMarkData(mark, self.lineno)
        else:
            if (not mark.tagname):
                mark = Mark('span', '', mark.classname, '', '')
            # assume generic closure
            d = MarkData(mark, TargetedMarkClosure, self.InlineOpenMark, self.lineno)
        self.markOpenPush(b, d)
        
        # slack between a tagname and the written content
        self.skipWhiteSpace()
                
        # And now a trick, though it is semantically consistent.
        if (mark.tagname == 'a' and self.cpPeek() == self.InlineCloseMark):
            # The open tag is written, the closure pushed.
            # but, if it's an anchor, and the next cp is an inline close
            # we have an anchor with no content, not even space.
            # in which case, we write the href to output, as anchor 
            # content
            b.extend(mark.href)
            
    def onInlineClose(self, b):
        self.expectedHeadPopClose(b, self.InlineOpenMark)
        
    def inlineBuilderWrite(self, b):
        l = ''.join(self.inlineB)
        if (self.uml):
            l = uml.all(l)
        b.append(l)
        self.inlineB = []
                
    def processInlineContent(self, b):
        # Basic attitude is, any code that calls this should setup 
        # linepos on the first character on the content. This 
        # method makes no attempt to guess or compensate for where
        # that position is.   For example, it will not skip whitespace.    
        #self.skipWhiteSpace()
        cp = self.cpGet()
        while (cp):
            if (cp == self.InlineOpenMark):
                # write down what we have
                self.inlineBuilderWrite(b)
                
                # Process the mark
                self.onInlineOpen(b, self.InlineOpenMark)
                
                # Now on a new cp. So we test from new...
                cp = self.cpGet()
                continue
            if (cp == self.InlineCloseMark):
                self.inlineBuilderWrite(b)
                self.onInlineClose(b)
                
                # Now on a new cp. So we test from new...
                cp = self.cpGet()
                continue
            self.inlineB.append(cp)
            cp = self.cpGet()
            
        # write anything left
        self.inlineBuilderWrite(b)
                            
    def paragraphOpenPush(self, b):
        markData = ParagraphMarkData(open_lineno=self.lineno)
        self.markOpenPush(b, markData)
        self.inPara = True

    def onPostBlockInlineContent(self, b):
        # Doesn't issue a closing signal.
        # This is slightly more efficient than running a close, when
        # it is known that a close has been run (after 
        # block marks). It is also necessary: an anonymous list can
        # halt on a start of inline text, so text in it's elements
        # must not fire an InlineStartSignal.
        c = self.skipWhiteSpace()
        
        # anything there?  Make a clean start
        if (c):
            self.paragraphOpenPush(b)
            self.processInlineContent(b)
                                    
    def onInlineStart(self, b):
        '''
        Start of non-block line.
        See also onPostBlockInlineContent()
        '''
        if (not self.inPara):
            # close anything reacting to this
            self.typeMatchPopClose(b, InlineStartSignal)

            # start the inline content
            self.paragraphOpenPush(b)
        else:
            # push the space corresponding to a newline
            b.append(' ')
        self.processInlineContent(b)
            
            
    # block level
    
    #? like anonymouse list items
    def onHeadlineControl(self, b):
        # It's a non-list element block
        # open or close, this is the end of phrase content.
        # signal
        self.typeMatchPopClose(b, BlockMarkSignal)
        level = 0
        c = self.cpGet()
        while (c and c == '='):
            level += 1
            c = self.cpGet()
        
        # Currently not scanning for attributes, and the crude grab
        # is stepped off what should be whitespace. But soak space.
        self.skipWhiteSpace()
        
        tagname = 'h' + str(level)
        b.append('<{}>'.format(tagname) )
        self.processInlineContent(b)
        b.append('</{}>'.format(tagname))

    #? like anonymouse list items
    def onImageControl(self, b):
        # It's a non-list element block
        # open or close, this is the end of phrase content.
        # signal
        self.typeMatchPopClose(b, BlockMarkSignal)

        # only do this to get attribute data
        # need to go past peeked control
        self.cpSkip()
        mark = self.parseAttributes(None)
        b.append(''.format(mark.href, mark.text) )
        caption = ""
        if (mark.text):
            caption = "<figcaption>" + mark.text + "</figcaption>"
        alt = 'image of ' + pathlib.Path(mark.href).stem
        klass = ''
        if (mark.classname):
            klass = ' class="' + mark.classname + '"'
        b.append('<figure {}><img src="{}" alt="{}"/>{}</figure>'.format(
            klass, 
            mark.href, 
            alt, 
            caption 
        ))
            
    def parseAndProcessBlockOpen(self, b, cntrlChar):
        '''
        Parse blockcontrol open
        Expects to start on  the cp following the control
        Ends on the delimiting whitespace
        Create, render and push data to the closeStack. 
        '''
        # parse blockcontrol
        # Note this finishes on the delimiting space        
        mark = self.parseAttributes(cntrlChar)
        #!!! Move this up to parsing attributes
        # OR, how do we avoid inlines??? OR do we avoid them?
        #if (mark.tagname in self.shortcutBlockTags):
        #    mark = Mark(self.shortcutBlockTags[mark.tagname], '', mark.classname, '', '')
        d = MarkData(mark, TargetedMarkClosure, cntrlChar, self.lineno)
        self.markOpenPush(b, d)
                
    def onBlockControl(self, b, control):
        '''
        Handle most Block controls, open or close
        Except list elements and escapes.
        
        '''
        # Non-list element hard-left controls arrive here.
        # The position is after the control
   
        # Open or close, close annon lists and inline content.
        self.typeMatchPopClose(b, BlockMarkSignal)
            
        # now handle blockmark
        nxt = self.cpPeek()
        if (not nxt or self.isWhitespace(nxt)):
            # close mark
            # if closing a list, fire off extra signal to finish
            # list elements
            if (control == '+'):
                self.typeMatchPopClose(b, ListCloseSignal)
            self.expectedHeadPopClose(b, control)
                            
            # munch the space
            self.cpGet()
        else:
            # open mark
            self.parseAndProcessBlockOpen(b, control)

    def onBlockEscapeOpenControl(self, b, cntrlChar):
        # If reach here must be an open control---see trigger code
        # Close annon lists and inline content.
        self.typeMatchPopClose(b, BlockMarkSignal)
        nxt = self.cpPeek()
        if (not nxt or self.isWhitespace(nxt)):
            # Not in escape, but not an open mark. Error
            raise ParseError(
                self.lineno, 
                "Unescaped markup contains escape close mark", 
                self.line
            )
        else:
            self.inEscape = True
                
            # open mark
            # Note this eats the delimiting space        
            mark = self.parseAttributes(cntrlChar)
            d = self.pre_markdata(mark, self.lineno)
            self.markOpenPush(b, d)                    
        
    def onBlockEscapeCloseControl(self, b, control):
        # Escape hard-left controls when esccaped arrive here.
        # The position is after the control       
        nxt = self.cpPeek()
        if (not nxt or self.isWhitespace(nxt)):
            # good close
            # close mark
            self.inEscape = False
                
            # munch the space
            #self.cpGet()
            self.expectedHeadPopClose(b, control)            
        else:
            # In escape, but not a close mark. Error
            raise ParseError(
                self.lineno, 
                "Escaped markup contains further escape open mark", 
                self.line
            )
                        
    def onListElementControl(self, b, control):
        # List element hard-left controls arrive here.
        # The position is after the control
        # only need one control, no parsing
        # The control is skipped.

        # close all self-closing blocks, includes previous list 
        # elements and inline content
        self.typeMatchPopClose(b, ListElementSignal)
        
        # if necessary, insert an implicit list  
        e = self.closeStack.head() 
        if(not e or (e.control != '+')):
            # signal closures
            self.typeMatchPopClose(b, BlockMarkSignal)
            
            # special block, closes on inline starts and non-list blocks 
            #! put somewhere configurable
            #?
            d = MarkData(Mark('ul', '', '', '', ''), InlineStartOrNonListBlockClosure, '+', open_lineno=self.lineno)
            self.markOpenPush(b, d)
            
            # update local head var
            e = d

        # skip the following char (should be space)
        #self.cpGet()
        self.cpSkip()

        # test the head/surrounding block for special anonymous closure
        if (e and e.closeType == InlineStartOrNonListBlockClosure):
            # an anonymous list element
            tagname = self.listElementTags[control]
            b.append('<{}><p>'.format(tagname) )
            self.processInlineContent(b)
            b.append('</p></{}>'.format(tagname))
        else:
            # handled as block-level tag
            tagname = self.listElementTags[control]
            d = MarkData(Mark(tagname, '', '', '', ''), ListElementOrCloseClosure, control, self.lineno)

            self.markOpenPush(b, d)
            self.onPostBlockInlineContent(b)

    def feed(self, b, line):
        '''
        Lines need to be right-stripped of trailing space, including newlines.
        '''
        self.lineno += 1
        self.line = line
        self.linepos = 0
        self.linelen = len(line)
        first_char = self.cpPeek()

        if (self.inEscape):
            if (first_char == '?'):
                # close
                #self.onBlockEscapeControl(b, self.cpGet())
                self.onBlockEscapeCloseControl(b, self.cpGet())
            else:
                # Escaped. Write in the line, no parsing
                b.append(conditional_escape(self.line))
                
                # append what would be there (but TML removes, usually)
                b.append('\n')
                                
        elif (first_char is None):
            # close down inline
            self.typeMatchPopClose(b, InlineStartSignal)
        elif (first_char in self.BlockSignificantMarks):
            self.onBlockControl(b, self.cpGet())
        elif (first_char == '='):
           self.onHeadlineControl(b)
        elif (first_char in self.BlockListElementMarks):
            self.onListElementControl(b, self.cpGet())
        elif (first_char == '*'):
           self.onImageControl(b)
        elif (first_char == '?'):
            # open only
            #self.onBlockEscapeControl(b, self.cpGet())
            self.onBlockEscapeOpenControl(b, self.cpGet())
        else:
            # Not a block, all whitespace, or escaped. Must be inline 
            # content.
            self.onInlineStart(b)
               
        
    def close(self, b):
        # close could focibly empty the stack.
        # Vut it's maybe more interesting to expose bracketting errors
        # not disgusise them. So use an InlineStartSignal, oddly, which
        # will close anonymous lists and paragraphs, so no need for a
        # trailing newline. But it will not fix unbalanced block marks. 
        self.typeMatchPopClose(b, InlineStartSignal)

        if (not self.closeStack.isEmpty):
            raise ParseError(
                self.lineno, 
                "Unclosed marks in source", 
                ', '.join([d.error_str() for d in self.closeStack.reverse()])
            )



class PreCodeBlockMarkData(MarkData):
    def __init__(self, mark, open_lineno=None):
        super().__init__(mark, TargetedMarkClosure, '?', open_lineno)
                  
    def open(self, b):
        #? class
        b.append('<figure><pre><code contenteditable spellcheck="false">')

    def close(self, b):
        b.append('</code></pre></figure>')    
        
class CodeBlockParser(Parser):
    pre_markdata = PreCodeBlockMarkData
        
        
        
        
class PreCodeBlockPrismMarkData(MarkData):
    '''
    Markup <pre> areas for code snippets highlighted with prism.js.
    '''
    def __init__(self, mark, open_lineno=None):
        # tagname used as language indicator
        super().__init__(mark, TargetedMarkClosure, '?', open_lineno)
                  
    def open(self, b):
        # no classname handling
        lang = 'none' if (self.mark.tagname == 'pre') else self.mark.tagname
        b.append('<figure><pre><code contenteditable spellcheck="false" class="language-{0}">'.format(lang))

    def close(self, b):
        b.append('</code></pre></figure>') 
        
class PrismParser(Parser):
    pre_markdata = PreCodeBlockPrismMarkData

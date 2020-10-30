from tml.utils import Stack
from tml import uml
from django.utils.html import conditional_escape
from collections import namedtuple


Mark = namedtuple('Mark', ['tagname', 'classname', 'href'])



class ParseError(Exception):
    def __init__(self, lineno, message, data=''):
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
    

class MarkInfo():
    # immutable mark info
    def __init__(self, mark, closeType, control):
        self.mark = mark 
        self.closeType = closeType
        self.control = control 
        
        
        
class MarkData():
    '''
    mark
        a parsed representation of a mark
    control
        the text mark which triggered creating this class
    '''
    def __init__(self, mark, closeType, control, open_lineno=None):
        self.mark = mark 
        self.closeType = closeType
        self.control = control 
        self.open_lineno = open_lineno

    @classmethod
    def from_generic(cls, info, open_lineno=None):
        '''Call as
           d = MarkData.from_generic(info, lineno)
        '''
        return cls(
            info.mark, 
            info.closeType, 
            info.control, 
            open_lineno=open_lineno
        )
        
    def open(self, b):
        if (self.mark.classname):
            b.append('<{} class="{}">'.format(self.mark.tagname, mark.classname))
        else:
            b.append('<{}>'.format(self.mark.tagname))

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
        super().__init__(Mark('p', '', ''), InlineStartOrBlockMarkClosure, '\\n', **kwargs)



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

    def open(self, b):
        if (self.mark.classname):
            b.append('<pre class="{}">'.format(self.mark.classname))
        else:
            b.append('<pre>')
            
    def close(self, b):
        b.append('</pre>')  



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
    }
    
    # Since no attributes currently accepted, can deliver complete 
    # MarkInfos
    shortcutListElementInfo = {
      '-' : MarkInfo(Mark('li', '', ''), ListElementOrCloseClosure, '-'),
      '~' : MarkInfo(Mark('dt', '', ''), ListElementOrCloseClosure, '~'),
      ':' : MarkInfo(Mark('dd', '', ''), ListElementOrCloseClosure, ':'),
    }

    #NB Not rendered through stack, or with attributes, so needs no 
    # MarkData
    anonymousShortcutListElementTags = { 
      '-': 'li',
      '~': 'dt',
      ':': 'dd',
    }
        
    #! uml should go aftretr TML, probably?
    def __init__(self, uml=False):
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
        Get a char from the stored line.
        A quiet function that throws no errors
        return
            A char. if at lineend, None
        '''
        r = None
        if (self.linepos < self.linelen):
            r = self.line[self.linepos]
            self.linepos += 1
        return r

    def cpPeek(self):
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

    def parseInlineControl(self):
        '''
        Eat input from current pos until whitespace.
        Note this is a tricky function. It eats a limiting 
        whitespace. It also will not error, returning as much as it can
        find. It stops quietly at lineends.
        '''
        tagclassnameB = []
        hrefB = []
        c = self.cpGet()
        while (c and not self.isWhitespace(c) and c != '('):
            tagclassnameB.append(c)
            c = self.cpGet()
            
        # now get tag and class names
        tagclassname =  ''.join(tagclassnameB) 
        splitC = tagclassname.split('.', 1)
        tagname = splitC[0]
        classname = ''
        if (len(splitC) > 1):
            classname = splitC[1] 
 
        # Now parse hrefs
        if (c == '('):
            c = self.cpGet()
            while (c and (c != ')')):
                hrefB.append(c)            
                c = self.cpGet()
            #self.cpGet()  
            self.cpSkip()  
        return Mark(tagname, classname, ''.join(hrefB))


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
        
    def onInlineOpen(self, b):
        # positioned on the char after the control
        mark = self.parseInlineControl()     
        if (mark.tagname == 'a'):
            d = AnchorMarkData(mark, self.lineno)
        else:
            if (not mark.tagname):
                mark = Mark('span', mark.classname, '')
            # assume generic closure
            d = MarkData(mark, TargetedMarkClosure, self.InlineOpenMark, self.lineno)                        
        # if (not mark.tagname):
            # # shortcut data available
            # info = self.shortcutMarkInfo[self.InlineOpenMark]
            # d = MarkData.from_generic(info, self.lineno)
        # elif (mark.tagname == 'a'):
            # d = AnchorMarkData(mark, self.lineno)
        # else:
            # # assume generic closure
            # d = MarkData(mark, TargetedMarkClosure, self.InlineOpenMark, self.lineno)
        self.markOpenPush(b, d)

    def onInlineClose(self, b):
        self.expectedHeadPopClose(b, self.InlineOpenMark)

    def processInlineContent(self, b):
        # used once set up for inline material
        self.skipWhiteSpace()
        if (self.uml):
            # We are beyond block tags, with only inlines to
            # consider.
            # Slice the line, as UML may tinker with overall length
            # and this ensures our start pos.
            self.line = uml.all(self.line[self.linepos:])
            self.linelen = len(self.line)
            self.linepos = 0
            
        p = self.cpGet()
        while (p):
            if (p == self.InlineOpenMark):
                self.onInlineOpen(b)
            
                # slack between a tagname and the written content. Must 
                # be one space, but may be more
                self.skipWhiteSpace()
            elif (p == self.InlineCloseMark):
                self.onInlineClose(b)
            else:
                b.append(p)
            p = self.cpGet()
                            
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
        # used at the start of non-block lines.
        # See also onPostBlockInlineContent()
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
        tagname = 'h' + str(level)
        b.append('<{}>'.format(tagname) )
        self.processInlineContent(b)
        b.append('</{}>'.format(tagname))

    def parse_mark_data(self, data):
        splitC = data.split('.', 1)
        tagname = splitC[0]
        classname = ''
        if (len(splitC) > 1):
            classname = splitC[1] 
        return Mark(tagname, classname, '')
        
    def parseAndProcessBlockOpen(self, b, control):
        '''
        Create, render and push data to the closeStack. 
        '''
        # parse blockcontrol
        # Note this eats the delimiting space        
        mark = self.parse_mark_data(self.getUntilWhiteSpace())
        if (mark.tagname in self.shortcutBlockTags):
            mark = Mark(self.shortcutBlockTags[mark.tagname], mark.classname, '')

        d = MarkData(mark, TargetedMarkClosure, control, self.lineno)
        
        # # convert shortcuts like '+' to MarkInfo, else make one
        # if (mark.tagname in self.shortcutMarkInfo):
            # # shortcut data available
            # info = self.shortcutMarkInfo[mark.tagname]
            # d = MarkData.from_generic(info, self.lineno)
        # else:
            # # assume generic closure
            # d = MarkData(mark, TargetedMarkClosure, control, self.lineno)
        self.markOpenPush(b, d)
                
    def onBlockControl(self, b, control):
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
                
            # munch the space
            #self.cpGet()
            self.expectedHeadPopClose(b, control)
        else:
            # open mark
            self.parseAndProcessBlockOpen(b, control)

    def onBlockEscapeControl(self, b, control):
        # Escape hard-left controls arrive here.
        # The position is after the control
        # Annoyingly different to generic block control handling,
        # especially due to breakout handling.
        
        # Open or close, close annon lists and inline content.
        self.typeMatchPopClose(b, BlockMarkSignal)
            
        # now handle blockmark
        nxt = self.cpPeek()
        if (not nxt or self.isWhitespace(nxt)):
            # close mark
            self.inEscape = False
                
            # munch the space
            #self.cpGet()
            self.expectedHeadPopClose(b, control)
        else:
            self.inEscape = True
                
            # open mark
            # Note this eats the delimiting space        
            mark = self.parse_mark_data(self.getUntilWhiteSpace())
            d = self.pre_markdata(mark, self.lineno)
            self.markOpenPush(b, d)
        
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
            d = MarkData(Mark('ul', '', ''), InlineStartOrNonListBlockClosure, '+', open_lineno=self.lineno)
            self.markOpenPush(b, d)
            
            # update local head var
            e = d

        # skip the following char (should be space)
        #self.cpGet()
        self.cpSkip()

        # test the head/surrounding block for special anonymous closure
        if (e and e.closeType == InlineStartOrNonListBlockClosure):
            # an anonymous list
            tagname = self.anonymousShortcutListElementTags[control]
            b.append('<{}><p>'.format(tagname) )
            self.processInlineContent(b)
            b.append('</p></{}>'.format(tagname))
        else:
            #info = self.shortcutMarkInfo[control]
            info = self.shortcutListElementInfo[control]
            d = MarkData.from_generic(info, self.lineno)
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

        if (first_char is None):
            # close down inline
            self.typeMatchPopClose(b, InlineStartSignal)
        elif (first_char in self.BlockSignificantMarks):
            self.onBlockControl(b, self.cpGet())
        elif (first_char == '='):
           self.onHeadlineControl(b)
        elif (first_char in self.BlockListElementMarks):
            self.onListElementControl(b, self.cpGet())
        elif (first_char == '?'):
            self.onBlockEscapeControl(b, self.cpGet())
        else:
            # Not a block, or any kind of whitespace. Must be inline 
            # content. 
            if (not self.inEscape):
                self.onInlineStart(b)
            else:
                # Escaped. Write in the line, no parsing
                b.append(conditional_escape(self.line))
                
                # append what would be there (but TML removes, usually)
                b.append('\n')                 
        
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
        lang = 'none' if (self.mark.tagname == '?') else self.mark.tagname
        b.append('<figure><pre><code contenteditable spellcheck="false" class="language-{0}">'.format(lang))

    def close(self, b):
        b.append('</code></pre></figure>') 
        
class PrismParser(Parser):
    pre_markdata = PreCodeBlockPrismMarkData

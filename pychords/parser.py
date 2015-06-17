from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment
#from xml.etree.ElementTree import _ElementInterface as ElementBase
from xml.etree.ElementTree import tostring as dumpElement

####        ####
#### parser ####
####        ####

class BadFormattingError(RuntimeError): pass
class BadDirectiveError(RuntimeError): pass
class NotFinishedError(RuntimeError): pass

class LineBegin(object): pass
class VerseBegin(object): pass
class TabBegin(object): pass
class ChorusBegin(object): pass

def set_meta(s, key, value):
    'Sets a key:value pair in the metadata at stack[0]'
    s[0][key] = value

def append_meta(s, key, value):
    'Appends a key:value pair to a list in the metadata at stack[0]'
    s[0][key] = s[0].get(key, []) + [value]

def pop_to_object(s, t):
    '''
    Scan stack "s" for "t", pop and return between "t" and end of stack.
    
    If item "t" is not found, then restore stack and return empty list.
    '''
    l = []
    try:
        while True:
            o = s.pop()
            if o == t:
                break
            l.insert(0, o)
    except IndexError:
        s.extend(l)
        l = []
    return l

def isElement(o):
    'Test wether "o" is an ElementTree.Element'
    # TODO: is there a better way to detect Element?
    #return o.__class__ is ElementBase
    return isinstance(o, Element)

def isComment(o):
    'Test wether "o" is an ElementTree.Comment'
    return isElement(o) and o.tag is Comment

def parse(tokens):
    'Returns an ElementTree-based DOM using output from tokenizer()'
    
    document = ElementTree(Element('chordpro'))
    root = document.getroot()
    head = SubElement(root, 'head')
    body = SubElement(root, 'body')
    stack = [{}, body] # bottommost stack member is the meta dict
    
    for (lineno, ttype, tvalue) in tokens:
        ttype = ttype.lower()
        if ttype == 'directive':
            # offload large if/else tree to directive_handler()
            directive_handler(tokens, stack, lineno, ttype, tvalue)
        elif ttype == 'comment':
            stack.append(Comment(tvalue))
        elif ttype == 'chord':
            # always maintain a chord:lyric pairing on the stack
            stack.append(Element('cho', {'c':tvalue.strip()}))
            stack[-1].text = ''
        elif ttype == 'lyric':
            # if a lyric appears before a chord, assume a blank chord
            tvalue = tvalue.lstrip()
            if tvalue:
                if not isElement(stack[-1]) or stack[-1].tag != 'cho':
                    stack.append(Element('cho', {'c':''}) )
                    stack[-1].text = ''
                stack[-1].text = stack[-1].text + tvalue
        elif ttype == 'sof':
            pass
        elif ttype == 'eof':
            eol_handler(tokens, stack, lineno, ttype, tvalue)
        elif ttype == 'sol':
            stack.append(LineBegin)
        elif ttype == 'eol':
            # offload large chunk of logic to eol_handler()
            # this is also where the parts of the DOM are moved from the 
            #   stack to the document
            eol_handler(tokens, stack, lineno, ttype, tvalue)
        else:
            raise BadFormattingError('Unrecognized token %r (%r) at line %d' % (ttype, tvalue, lineno))
    
    # time to stuff metadata into the document's <head> tag
    meta = stack[0]
    if 'title' in meta:
        e = Element('title')
        e.text = meta['title']
        head.append(e)
    if 'subtitle' in meta:
        e = Element('subtitle')
        e.text = meta['subtitle']
        head.append(e)
    if 'define' in meta and len(meta['define']):
        for d in meta['define']:
            e = Element('define')
            e.text = d
            head.append(e)

    return document

def eol_handler(tokens, stack, lineno, ttype, tvalue):
    '''
    Parser handler of end-of-line and end-of-file events
    
    This is largely where elements are moved from the stack and put into
    the document.
    '''
    
    line = pop_to_object(stack, LineBegin)
    
    if len(line):
        if not all(isComment(e) for e in line):
            r = Element('row')
            stack.append( r )
            for e in line:
                r.append(e)
        else:
            # current line contains nothing but Comment objects
            stack.extend(line)
    
    else:
        # odds are we're currently parsing a blank line
        # - which is used to separate verse blocks
        in_chorus = False
        for o in reversed(stack):
            if o is ChorusBegin:
                in_chorus = True
                break
        
        # if we're in a chrous, stay in chorus mode
        # else, stop verse and start new verse
        if not in_chorus:
            verse = pop_to_object(stack, VerseBegin)
            
            if verse:
                v = Element('verse')
                stack[1].append( v )
                for e in verse:
                    v.append(e)
            
            else:
                # we're not in a verse, so move everything from the 
                #   stack to the document
                l = []
                while len(stack) > 2 and isElement(stack[-1]):
                    l.insert(0, stack.pop())
                for e in l:
                    stack[1].append(e)
            
            stack.append(VerseBegin)

def directive_handler(tokens, stack, lineno, ttype, tvalue):
    'Parser handler for all directives'
    
    tag, arg = tvalue.split(':', 1) if ':' in tvalue else (tvalue, '')
    tag = tag.lower()
    
    if tag in ('t', 'title'):
        if not arg: raise BadDirectiveError('{%s} directive needs an argument at line %s' % (tag, lineno))
        set_meta(stack, 'title', arg)
    
    elif tag in ('st', 'subtitle'):
        if not arg: raise BadDirectiveError('{%s} directive needs an argument at line %s' % (tag, lineno))
        set_meta(stack, 'subtitle', arg)
    
    elif tag == 'define':
        if not arg: raise BadDirectiveError('{%s} directive needs an argument at line %s' % (tag, lineno))
        append_meta(stack, 'define', arg)
    
    elif tag in ('c', 'comment'):
        if not arg: raise BadDirectiveError('{%s} directive needs an argument at line %s' % (tag, lineno))
        c = Element('comment')
        c.text = arg
        stack[1].append( c )
    
    elif tag in ('ci', 'comment_italic'):
        if not arg: raise BadDirectiveError('{%s} directive needs an argument at line %s' % (tag, lineno))
        stack.append( Element('comment', {'italic':'true'}) )
        stack[-1].text = arg
    
    elif tag in ('cb', 'comment_box'):
        if not arg: raise BadDirectiveError('{%s} directive needs an argument at line %s' % (tag, lineno))
        stack.append( Element('comment', {'box':'true'}) )
        stack[-1].text = arg
    
    elif tag in ('soc', 'start_of_chorus'):
        # close the current verse, if any, then start a chorus
        if arg: raise BadDirectiveError('{%s} directive needs no argument %r at line %d' % (tag, arg, lineno))
        pop_to_object(stack, LineBegin)
        verse = pop_to_object(stack, VerseBegin)
        if verse:
            v = Element('verse')
            stack.append( v )
            for e in verse:
                v.append(e)
        stack.append(ChorusBegin)
    
    elif tag in ('eoc', 'end_of_chorus'):
        # close the current chorus, but don't start a verse
        # - that's done after an sol token
        if arg: raise BadDirectiveError('{%s} directive needs no argument %r at line %d' % (tag, arg, lineno))
        pop_to_object(stack, LineBegin)
        c = Element('chorus')
        stack[1].append( c )
        chorus = pop_to_object(stack, ChorusBegin)
        for e in chorus:
            c.append(e)
    
    elif tag == 'tab':
        if not arg: raise BadDirectiveError('{%s} directive needs an argument at line %s' % (tag, lineno))
        t = Element('tab')
        t.text = arg
        stack[1].append( t )
    
    elif tag in ('np', 'new_page', 'npp', 'new_physical_page',
                                                  'ns', 'new_song', 'rowname'):
        # haven't implemented these yet, don't want them throwing errors either
        # ...they're basically just rendering hints anyway
        pass
    
    else:
        # TODO: do we need a catchall for {directive}?
        # TODO: directives seen in other parsers:
        # TODO: - textfont, textsize
        # TODO: - chordfont, chordsize
        # TODO: - ng, no_grid
        # TODO: - g, grid
        raise NotFinishedError('Unimplemented directive %s at line %d' % (tag, lineno))





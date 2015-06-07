import re

from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment
from xml.etree.ElementTree import _ElementInterface as ElementBase
from xml.etree.ElementTree import tostring as dumpElement

def tokenize(infile):
    '''
    Splits bytes from infile into tokens for the parser.
    
    Returns an iterator which delivers tokens in the tuple form:
        (line number, token type, token value)
    
    There are currently 8 token types:
    'directive': chordpro directives, found in {curly braces}; the token
        value will be the full text of the directive including the
        arguments, if any - also note that unparsed {tab} contents are 
        returned as the argument to a {tab} directive
    'chord': inline chord notation, found in [square brackets]
    'comment': sh-style source-code comment, found between an octothorpe
        and the end of line - not to be confused with a sharp symbol, 
        which is found in a chord token using the same character - also
        do not confuse this kind of comment with a chordpro-style
        {comment} directive, which is actually a text block
    'lyric': just about any other kind of text
    'sof', 'eof': start of file, end of file
    'sol', 'eol': start of line, end of line
    '''
    
    tokentypes = (
        'directive', 
        'chord',
        'comment',
        'lyric',
    )
    
    # pattern.findall(line) returns tuples of form 
    #   (directive, chord, comment, lyric)
    #   where only one is not an empty string
    pattern = re.compile(r'''
        \s* \{ ( [^}]+ ) \} # directive (meta or block)
    |
        \[ ( [^\]]+ ) \]    # chord
    |
        \s* \#  ( .+ )      # comment - only if # is not in chord or directive
    |
        ( [^[]+ )           # lyric
    ''', re.VERBOSE)
    
    yield (1, 'sof', '')
    # wrap readlines() in iterator so can be passed to preformatted_tokenizer()
    lines = iter(enumerate(infile.readlines()))
    
    for lineno, line in lines:
        yield (lineno+1, 'sol', '')
        
        line = line.rstrip()
        for tokens in pattern.findall(line):
            (ttype, tvalue) = [
                t
                for t 
                in zip(tokentypes, tokens) 
                if t[1] != ''
            ][0]
            if ttype == 'directive' and tvalue in ('sot', 'start_of_tab'):
                tvalue = preformatted_tokenize(lines, 
                                               r'^\s*\{(eot|end_of_tab)\}\s*$')
                tvalue = 'tab:' + ''.join([v[1] for v in tvalue])
            yield (lineno+1, ttype, tvalue)
        
        yield (lineno+1, 'eol', '')
    
    yield (lineno+1, 'eof', '')


def preformatted_tokenize(lines, pattern):
    'Returns untokenized text from iterator "lines"'
    pattern = re.compile(pattern, re.I)
    for lineno, line in lines:
        if not pattern.match(line):
            yield lineno, line
        else:
            return




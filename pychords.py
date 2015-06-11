# https://bitbucket.org/holms/chordpro/

import argparse
import re
import string
import sys

import pychords.tokenizer 
import pychords.parser 
import pychords.render
from pychords.render2pdf import Render2Pdf
 
def parseInput(filename, format):
    chordfile = open(filename)
    tokens = pychords.tokenizer.tokenize(chordfile)
    document = pychords.parser.parse(tokens)

    if format=='text' :
        for line in pychords.render.renderToAscii(document):
            print (line)
    elif format=='html' :
        for line in pychords.render.renderToHtmlTables(document):
            print (line)
    elif format=='pdf':
        render = Render2Pdf()
        render.render(document)
    elif format=='html_css' :
        for line in pychords.render.renderToHtmlCss(document):
            print (line)
    
def main():
    parser = argparse.ArgumentParser(
        description='Tool for processing song lyrics stored in ChordPro formatted files')
    parser.add_argument('files', help='chordpro file to be processed')
    parser.add_argument('-f', help='Output format (supported is text, html, html_css and pdf)', default='text')
    args = parser.parse_args()
    
    output = None
    verbose = False

    if args.f not in ['text', 'html', 'html_css', 'pdf']:
        sys.stderr.write('Unsupported format %s\n' % str(args.f))
        sys.exit(1)
    
    # Pass params to chordpro class
    parseInput(args.files, args.f)

if __name__ == "__main__":
    main()

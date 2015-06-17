# https://bitbucket.org/holms/chordpro/

import argparse
import os
import re
import string
import sys
import codecs

from . import tokenizer, parser, render, render2pdf
 
def parseInput(filename, styleSheet, format):
    (root, ext) = os.path.splitext(filename)
    chordfile = codecs.open(filename, 'r', 'utf-8-sig')
    tokens = tokenizer.tokenize(chordfile)
    document = parser.parse(tokens)

    if format=='text' :
        for line in render.renderToAscii(document):
            print (line)
    elif format=='html' :
        for line in render.renderToHtmlTables(document):
            print (line)
    elif format=='pdf':
        fileNameOutput = root + '.pdf'
        render = render2pdf.Render2Pdf(fileNameOutput, styleSheet)
        render.render(document)
    elif format=='html_css' :
        for line in render.renderToHtmlCss(document):
            print (line)
    
def main():
    parser = argparse.ArgumentParser(
        description='Tool for processing song lyrics stored in ChordPro formatted files')
    parser.add_argument('files', help='chordpro files to be processed', nargs='+', metavar='file')
    parser.add_argument('-f', choices=['text', 'html', 'html_css', 'pdf'], help='Output format', default='text')
    parser.add_argument('-s', help='Style sheet file')
    args = parser.parse_args()
    
    output = None
    verbose = False

    if args.f not in ['text', 'html', 'html_css', 'pdf']:
        sys.stderr.write('Unsupported format %s\n' % str(args.f))
        sys.exit(1)

    # initialize style-sheet
    styleSheet = render2pdf.StyleSheet()
    if args.s:
        styleSheet.loadFromFile(args.s)

    # Pass params to chordpro class
    for f in args.files:
        parseInput(f, styleSheet, args.f)


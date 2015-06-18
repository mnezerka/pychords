# https://bitbucket.org/holms/chordpro/

import argparse
import os
import re
import string
import sys
import codecs

from . import tokenizer, parser, render, render2pdf

def getDocumentTitle(d):
    head = d.find('head')
    title = head.find('title')
    if title != None:
        return title.text.strip()
    return "" 
     
def main():
    """Main for command line interface"""

    argParser = argparse.ArgumentParser(
        description='Tool for processing song lyrics stored in ChordPro formatted files')
    argParser.add_argument('files', help='chordpro files to be processed', nargs='+', metavar='file')
    argParser.add_argument('-f', choices=['text', 'html', 'html_css', 'pdf'], help='Output format', default='text')
    argParser.add_argument('-s', help='Style sheet file')
    argParser.add_argument('-n', help='Output name (name of the output file)')
    argParser.add_argument('-o', choices=['none', 'title', 'file'], help='Order before rendering', default='none')
    args = argParser.parse_args()
    
    # check arguments - format
    if args.f not in ['text', 'html', 'html_css', 'pdf']:
        sys.stderr.write('Unsupported format %s\n' % str(args.f))
        sys.exit(1)

    # initialize style-sheet
    styleSheet = render2pdf.StyleSheet()
    if args.s:
        styleSheet.loadFromFile(args.s)

    # generate output name
    outputName = None
    if args.n:
        outputName = args.n    
    # if no name is specified, take name of the first file
    elif len(args.files) > 0:
        (root, ext) = os.path.splitext(os.path.basename(args.files[0]))
        outputName = root
    else:
        sys.stderr.write('No files to be processed')
        sys.exit(1)

    # parse all files 
    documents = []
    for f in args.files:
        print('Reading "%s"' % f)
        chordfile = codecs.open(f, 'r', 'utf-8-sig')
        try:
            tokens = tokenizer.tokenize(chordfile)
            document = parser.parse(tokens)
            documents.append(document)
        except parser.NotFinishedError as e:
            print(f, e)

    # order before rendering
    if args.o == 'title':
        # order all documents according to title
        print('Sorting songs according to title')
        documents.sort(key = lambda d: getDocumentTitle(d))
         
    # render all documents
    print('Rendering to', args.f)
    if args.f == 'text' :
        for line in render.renderToAscii(documents):
            print (line)
    elif args.f == 'html' :
        for line in render.renderToHtmlTables(documents):
            print (line)
    elif args.f == 'pdf':
        fileNameOutput = outputName + '.pdf'
        render = render2pdf.Render2Pdf(fileNameOutput, styleSheet)
        render.render(documents)
    elif args.f == 'html_css' :
        for line in render.renderToHtmlCss(documents):
            print (line)


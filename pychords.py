# https://bitbucket.org/holms/chordpro/

import getopt
import re
import string
import sys

import pychords.tokenizer 
import pychords.parser 
import pychords.render
 
def parse_input(filename, format, smallgrid):
    chordfile = open(filename)
    tokens = pychords.tokenizer.tokenize(chordfile)
    document = pychords.parser.parse(tokens)

    if format=='text' :
        for line in pychords.render.renderToAscii(document, smallgrid=smallgrid):
            print (line)
    elif format=='html' :
        for line in pychords.render.renderToHtmlTables(document):
            print (line)
    elif format=='pdf':
        pychords.render.renderToPDF(document)
    elif format=='html_css' :
        for line in pychords.render.renderToHtmlCss(document):
            print (line)
    
def usage():
    print ("\nUsage: chordpro.py [-f format] [-s smallgrid] <file> ...\n")

def main():
    
    # Default shell params
    format    = "text"
    smallgrid = False
    
    # Collect shell params
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:s:h", ["format=", "smallgrid=", "help"])
        assert args
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    except AssertionError:
        usage()
        sys.exit(0)
    
    output = None
    verbose = False
    
    # Check shell params
    for o, a in opts:
        if   o in ("-f", "--format"):
            format = (a in ['text', 'html', 'html_css', 'pdf'] and a) or format
        elif o in ("-s", "--smallgrid"):
            if(a): smallgrid = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            print ("Unknown parameter given")
            sys.exit(0)
   
    # Pass params to chordpro class
    for file in args:
        parse_input(file, format=format, smallgrid=smallgrid)

if __name__ == "__main__":
    main()

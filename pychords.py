# https://bitbucket.org/holms/chordpro/

import getopt
import re
import string
import sys

from pychords import *
 
def parse_input(filename, format, smallgrid):
    chordfile = open(filename)
    tokens = tokenize(chordfile)
    document = parse(tokens)

    if format=='text' :
        for line in renderToAscii(document, smallgrid=smallgrid):
            print (line)
    elif format=='html' :
        for line in renderToHtmlTables(document):
            print (line)
    elif format=='html_css' :
        for line in renderToHtmlCss(document):
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
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    except AssertionError:
        usage()
        sys.exit(0)
    
    output = None
    verbose = False
    
    # Check shell params
    for o, a in opts:
        if   o in ("-f", "--format"):
            format = (a in ['text', 'html', 'html_css'] and a) or format
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

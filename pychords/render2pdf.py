import xml.sax.saxutils
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics

def safeText(s, html=False):
    'Sanitizes text from unknown 3rd parties during rendering'
    # TODO: no, really, sanitize text please
    if html:
        return xml.sax.saxutils.escape(s, {' ': '&nbsp;'})
    return s

def getStringExtent(str, fontName, fontSize):
    face = pdfmetrics.getFont(fontName).face
    ascent = (face.ascent * fontSize) / 1000.0
    descent = (face.descent * fontSize) / 1000.0
    height = ascent - descent # <-- descent it's negative
    width = stringWidth(str, fontName, fontSize)
    return (width, height)

def render(document):
    '''
    Renders a chordpro document into PDF file.
    '''
    marginLeft = 0
    marginTop = 0

    root = document.getroot()
    head = root.find('head')
    body = root.find('body')

    c = canvas.Canvas('song.pdf', bottomup = 0, pagesize=A4)
    pageWidth, pageHeight = A4

    fontName = 'Helvetica'

    fontTitleSize = 18 
    fontLyricSize = 10 
    fontChordSize = 10 

    #draw a box 10 wide and "height" tall
    #canv.rect(50,600 - descent,10,height) # <--to keep the baseline at 600

    #Write the string next to the box, it should be the exact same height
    #canv.setFont(fontname, fontsize) # <-- fix the size of your output text
    #canv.drawString(62,600,'Testing')

    posY = marginTop 

    # render title and subtitle, widely spaced if possible
    if head.find('title') != None:
        title = safeText(head.find('title').text).strip()
        box = getStringExtent(title, fontName, fontTitleSize)
        c.setFont(fontName, fontTitleSize)
        #print (stringWidth(title, 'Helvetica', 10))
        c.drawString(marginLeft, posY + box[1], title)
        posY += 30 

    if head.find('subtitle') != None:
        c.setFont(fontName, fontLyricSize)
        subtitle = safeText(head.find('subtitle').text).strip()
        c.drawString(marginLeft, posY, title)
        posY += 30

    c.setFont(fontName, fontLyricSize)

    # render each block (verse, chorus, tab, comment)
    for block in body:
        if block.tag in ('verse', 'chorus'):
            for line in block:
                posX = marginLeft 
                print(line.tag)

                if line.tag == 'row':
                    # split the row into a two-row table:
                    #   top row is chord names, padded on right with one space
                    #   bottom row is lyrics, use ... if no textual content
                    # use wrapper list "rows" so we can overflow line-wraps
                    chordRow = [safeText(cho.attrib.get('c', '')) for cho in line]
                    textRow = [safeText(cho.text) if cho.text else '... ' for cho in line]

                    for item in zip(textRow, chordRow):
                        print(item)
                        textBox = getStringExtent(item[0], fontName, fontLyricSize)
                        chordBox = getStringExtent(item[1], fontName, fontChordSize)
                        # draw chord
                        c.drawString(posX, posY, item[1])
                        # draw lyrics 
                        c.drawString(posX, posY + chordBox[1], item[0])
                        posX += textBox[0]
                    posY += textBox[1] * 3

                    #for i, d in rows

                    # get each column's max width
                    #widths = [map(max, zip( *[[len(item) for item in subrow] for subrow in row])) for row in rows]

                    #print(widths)
                else:
                    print('todo')

    c.showPage()
    c.save()

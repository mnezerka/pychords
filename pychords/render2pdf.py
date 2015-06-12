import xml.sax.saxutils
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
import reportlab.rl_config
#reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pkg_resources import resource_filename

def safeText(s, html=False):
        'Sanitizes text from unknown 3rd parties during rendering'
        # TODO: no, really, sanitize text please
        if html:
            return xml.sax.saxutils.escape(s, {' ': '&nbsp;'})
        return s

class StyleSheet:
    '''Visual definition of song typesetting'''
    def __init__(self):
        self.fontLyrics = ('Helvetica', 10)
        self.fontChords = ('Helvetica', 8)
        self.fontTitle = ('Helvetica', 20)
        self.fontSubTitle = ('Helvetica', 12)

class Render2Pdf:
    def __init__(self, fileName):
        self.fileName = fileName
        self.cFontName = 'Helvetica' 
        self.cFontSize = 10 
        self.canv = canvas.Canvas(self.fileName, bottomup = 0, pagesize=A4)
        self.pageWidth, self.pageHeight = A4
        self.marginLeft = 50 
        self.marginTop = 40 
        self.offsetPara = 10
        self.style = StyleSheet()

        hvFont = resource_filename(__name__, 'fonts/hv.ttf')
        pdfmetrics.registerFont(TTFont('Helvetica', hvFont))

        hvObliqueFont = resource_filename(__name__, 'fonts/hv-oblique.ttf')
        pdfmetrics.registerFont(TTFont('HelveticaOblique', hvObliqueFont))

    def getStringExtent(self, str, fontName = None, fontSize = None):
        fontName = fontName if fontName is not None else self.cFontName
        fontSize = fontSize if fontSize is not None else self.cFontSize
        face = pdfmetrics.getFont(fontName).face
        ascent = (face.ascent * fontSize) / 1000.0
        descent = (face.descent * fontSize) / 1000.0
        height = ascent - descent # <-- descent it's negative
        width = stringWidth(str, fontName, fontSize)
        return (width, height)

    def setFont(self, font):
        self.cFont= font
        try:
            self.canv.setFont(self.cFont[0], self.cFont[1])
        except:
            pass

    def drawString(self, x, y, string, fontName = None, fontSize = None):
        fontName = fontName if fontName is not None else self.cFontName
        fontSize = fontSize if fontSize is not None else self.cFontSize
        box = self.getStringExtent(string.encode('utf-8'), fontName, fontSize)
        self.canv.drawString(x, y + box[1], string)
        return box

    def render(self, document):
        '''
        Renders a chordpro document into PDF file.
        '''
        root = document.getroot()
        head = root.find('head')
        body = root.find('body')

        posY = self.marginTop 

        # render title
        if head.find('title') != None:
            title = safeText(head.find('title').text).strip()
            self.setFont(self.style.fontTitle)
            strSize = self.drawString(self.marginLeft, posY, title)
            posY += 30 

        # render subtitle
        if head.find('subtitle') != None:
            subtitle = safeText(head.find('subtitle').text).strip()
            self.setFont(self.style.fontSubTitle)
            strSize = self.drawString(self.marginLeft, posY, subtitle)
            posY += 30

        self.setFont(self.style.fontLyrics)

        # render each block (verse, chorus, tab, comment)
        for block in body:
            if block.tag in ('verse', 'chorus'):
                # prepare all rows of the block - each row has two lines 
                #   top row is chord names, padded on right with one space
                #   bottom row is lyrics, use ... if no textual content
                blockRows = []
                blockHasChords = False
                for line in block:
                     if line.tag == 'row':
                        row = [
                            [safeText(cho.attrib.get('c', '')) for cho in line],
                            [safeText(cho.text) if cho.text else ' ' for cho in line]
                        ]
                        blockRows.append(row)

                        # look for any chord if not found already
                        if not blockHasChords:
                            for c in row[0]:
                                if len(c) > 0:
                                    blockHasChords = True
                                    break
                    
                # draw paragraph

                # rendering of rows 
                for row in blockRows:
                    posX = self.marginLeft 
                    for item in zip(row[1], row[0]):
                        #print(item)
                        # draw chord
                        lyricOffsetY = 0
                        chordBox = (0, 0)
                        if blockHasChords:
                            self.setFont(self.style.fontChords)
                            chordBox = self.drawString(posX, posY, item[1])
                            lyricOffsetY = chordBox[1]

                        # draw lyrics 
                        self.setFont(self.style.fontLyrics)
                        textBox = self.drawString(posX, posY + lyricOffsetY, item[0])
                        posX += max(textBox[0], chordBox[0])

                    posY += lyricOffsetY + textBox[1]
                    posY += 5 

                posY += self.offsetPara

        self.canv.showPage()

        self.canv.save()



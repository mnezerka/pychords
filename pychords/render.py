import urllib
import xml.sax.saxutils


def safeText(s, html=False):
    'Sanitizes text from unknown 3rd parties during rendering'
    # TODO: no, really, sanitize text please
    if html:
        return xml.sax.saxutils.escape(s, {' ': '&nbsp;'})
    return s

    
####                 ####
#### Render to ASCII ####
####                 ####


def renderToAscii(document, 
                  width = 79, 
                  show_chords = True,
                  show_undefined_chords = True,
                  chord_catalog = None,
                  chord_gap = '   ', 
                  chorus_indent = '    ',
                  smallgrid=False):
    '''
    Renders a chordpro document into readable ASCII text.
    
    width parameter is how many characters wide to stay within
    
    chord_gap parameter is the space between chord grids within the same row
    
    chorus_indent parameter is, well, should be bloody obvious
    '''

    root = document.getroot()
    head = root.find('head')
    body = root.find('body')
    title, subtitle, defines = None, None, []
    if not chord_catalog:
        chord_catalog = {}

    # render title and subtitle, widely spaced if possible
    if head.find('title') != None:
        title = safeText(head.find('title').text).strip()
        if len(title) < width / 2:
            title = ' '.join(title)
        yield title.center(width)
        yield ''
    if head.find('subtitle') != None:
        subtitle = safeText(head.find('subtitle').text).strip()
        if len(subtitle) < width / 2:
            subtitle = ' '.join(subtitle)
        yield subtitle.center(width)
        yield ''
    
    # render each block (verse, chorus, tab, comment)
    for block in body:
    
        if block.tag in ('verse', 'chorus'):
            indent = ''
            if block.tag == 'chorus':
                indent = chorus_indent
            
            for line in block:
                
                if line.tag == 'row':
                    # split the row into a two-row table:
                    #   top row is chord names, padded on right with one space
                    #   bottom row is lyrics, use ... if no textual content
                    # use wrapper list "rows" so we can overflow line-wraps
                    rows = [
                        [
                            [
                                safeText(cho.attrib.get('c', '')) + ' ' 
                                for cho 
                                in line
                            ],
                            [
                                safeText(cho.text) if cho.text else '... ' 
                                for cho 
                                in line
                            ]
                        ]
                    ]
                    # get each column's max width
                    widths = [
                        map(max, zip(
                            *[[len(ii) for ii in i] for i in row]
                        ))
                        for row
                        in rows
                    ]
                    # commence line-wrapping
                    for r, row in enumerate(rows):
                        for i, row_widths in enumerate(widths):
                            if sum(row_widths) > width:
                                rows.insert(r+1, [[''],['']])
                                widths.insert(r+1, [len(chorus_indent)])
                                # move 2 cells minimum to new row
                                for a in (1, 2):
                                    rows[r+1][0].insert(1, rows[r][0].pop())
                                    rows[r+1][1].insert(1, rows[r][1].pop())
                                    widths[r+1].insert(1, widths[r].pop())
                                # while the line is too long
                                #   or the break is mid-lyric-word
                                while sum(row_widths) > width or \
                                                  not row[1][-1].endswith(' '):
                                    rows[r+1][0].insert(1, rows[r][0].pop())
                                    rows[r+1][1].insert(1, rows[r][1].pop())
                                    widths[r+1].insert(1, widths[r].pop())
                    # each column gets template string based on width
                    templates = [
                        ['%%-%ds' % i for i in row_widths]
                        for row_widths 
                        in widths
                    ]
                    for r in range(len(rows)):
                        # yield the chord names row
                        yield indent + ''.join([
                            t % i
                            for (t, i) 
                            in zip(templates[r], rows[r][0])
                        ])
                        # yield the lyrics row
                        yield indent + ''.join([
                            t % i 
                            for (t, i) 
                            in zip(templates[r], rows[r][1])
                        ])
                
                elif line.tag == 'comment':
                    # TODO: implement me - italics, box
                    yield block.text
                
                else:
                    # TODO: what other tags at this level?
                    # TODO: - ElementTree.Comment
                    pass
            
            # end of the block... blank line
            yield ''
        
        elif block.tag == 'comment':
            # TODO: implement me - italics, box
            yield block.text
        
        elif block.tag == 'tab':
            yield block.text
        
        else:
            # TODO: what other tags at this level?
            # TODO: - ElementTree.Comment
            pass

    
####                                                   ####
#### Render to HTML using <table> for lyric/chord rows ####
####                                                   ####


def renderToHtmlTables(document, 
                       basename = '',
                       show_chords = True,
                       show_undefined_chords = True,
                       chord_catalog = None):
    
    root = document.getroot()
    head = root.find('head')
    body = root.find('body')
    title, subtitle, defines = None, None, []
    if not chord_catalog:
        chord_catalog = {}
    
    yield '<html>'
    
    yield '<head>'
    if head.find('title') != None:
        yield '<title>%s</title>' % safeText(head.find('title').text.strip())
    yield '''
        <style type="text/css">
            h1, h2 { text-align: center }
            .defines img { vertical-align: top; padding: 0px; margin: 0px }
            div.chorus table { margin-left: 2em }
            div.chorus, div.verse, div.defines { padding-bottom: 1em }
            td.chord { color: #006; font-weight: bold; }
            td.lyric { white-space: pre; font-size: 120% }
            div.comment { font-weight: bold; color: #6f6; margin-bottom: 1em }
        </style>
    '''
    yield '</head>'
    
    yield '<body>'
    
    if head.find('title') != None:
        yield '<h1>%s</h1>' % safeText(head.find('title').text.strip(), html=True)
    if head.find('subtitle') != None:
        yield '<h2>%s</h2>' % safeText(head.find('subtitle').text.strip(), html=True)
    
    # render each block (verse, chorus, tab, comment)
    for block in body:
        
        if block.tag in ('verse', 'chorus'):
        
            yield '<div class="%s">' % block.tag
            
            for line in block:
            
                if line.tag == 'row':
                
                    yield '<table %s>' % (
                        ' '.join([
                            'border=0',
                            'cellpadding=0',
                            'cellspacing=0',
                            #'style="display:inline"',
                        ]),
                    )
                    yield '<tr>'
                    yield ''.join(
                        '<td class="chord">%s</td>' % safeText(cho.attrib.get('c', ''), html=True)
                        for cho
                        in line
                    )
                    yield '</tr>'
                    yield '<tr>'
                    yield ''.join(
                        '<td class="lyric">%s</td>' % safeText(cho.text if cho.text else '. . . ', html=True)
                        for cho
                        in line
                    )
                    yield '</tr>'
                    yield '</table>'
                    
                elif line.tag == 'comment':
                    # TODO: implement me - italics, box
                    yield '<div class="comment">%s</div>' % safeText(block.text, html=True)
                    
                else:
                    # TODO: what other tags at this level?
                    # TODO: - ElementTree.Comment
                    pass
            
            yield '</div>'
            
        elif block.tag == 'comment':
            # TODO: implement me - italics, box
            yield '<div class="comment">%s</div>' % safeText(block.text, html=True)
        
        elif block.tag == 'tab':
            yield '<pre>%s</pre>' % safeText(block.text, html=True)
        
        else:
            # TODO: what other tags at this level?
            # TODO: - ElementTree.Comment
            pass
    
    yield '</body>'
    
    yield '</html>'


####                                                        ####
#### Render to HTML using <div> and cssfor lyric/chord rows ####
####                                                        ####


def renderToHtmlCss(document, 
                    basename = '',
                    show_chords = True,
                    show_undefined_chords = True,
                    chord_catalog = None):
    
    root = document.getroot()
    head = root.find('head')
    body = root.find('body')
    title, subtitle, defines = None, None, []
    if not chord_catalog:
        chord_catalog = {}
    
    yield '<html>'
    
    yield '<head>'
    if head.find('title') != None:
        yield '<title>%s</title>' % safeText(head.find('title').text.strip())
    # TODO: fix this broken CSS
    # TODO: - rows that start with a chord-less lyric
    # TODO: - oh, and merge two cells where the first cell's lyric lacks trailing whitespace
    yield '''
        <style type="text/css">
            h1, h2 { text-align: center }
            .defines img { vertical-align: top; padding: 0px; margin: 0px }
            .chorus { margin-left: 2em }
            .chorus, .verse { clear: left; margin-bottom: 1em }
            .row { clear: left }
            .chord_lyric { float: left; vertical-align: bottom }
            .chord { color: #006; font-weight: bold }
            .lyric { white-space: pre; vertical-align: bottom; font-size: 120% }
            .comment { font-weight: bold; color: #6f6; margin-bottom: 1em; clear: left }
        </style>
    '''
    yield '</head>'
    
    yield '<body>'
    
    if head.find('title') != None:
        yield '<h1>%s</h1>' % safeText(head.find('title').text.strip(), html=True)
    if head.find('subtitle') != None:
        yield '<h2>%s</h2>' % safeText(head.find('subtitle').text.strip(), html=True)
    
    # render each block (verse, chorus, tab, comment)
    for block in body:
        
        if block.tag in ('verse', 'chorus'):
        
            yield '<div class="%s">' % block.tag
            
            for line in block:
            
                if line.tag == 'row':
                
                    yield '<div class="row">'
                    for cho in line:
                        yield \
                            '<div class="chord_lyric">' \
                            '<div class="chord">%s</div>' \
                            '<div class="lyric">%s</div>' \
                            '</div>' % (
                                safeText(cho.attrib.get('c', ''), html=True),
                                safeText(cho.text if cho.text else '. . . ', html=True)
                            )
                    yield '</div>'
                    
                elif line.tag == 'comment':
                    # TODO: implement me - italics, box
                    yield '<div class="comment">%s</div>' % safeText(block.text, html=True)
                    
                else:
                    # TODO: what other tags at this level?
                    # TODO: - ElementTree.Comment
                    pass
            
            yield '</div>'
            
        elif block.tag == 'comment':
            # TODO: implement me - italics, box
            yield '<div class="comment">%s</div>' % safeText(block.text, html=True)
        
        elif block.tag == 'tab':
            yield '<pre>%s</pre>' % safeText(block.text, html=True)
        
        else:
            # TODO: what other tags at this level?
            # TODO: - ElementTree.Comment
            pass
    
    yield '</body>'
    
    yield '</html>'

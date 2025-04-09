import inspect
import re
import string
import sys

editions = 'RCOAFN'

class Diff:
    def __init__(self, line, lines):
        self.lines = []

        _, lno, text = re.split(r'^([0-9]+) ', line)
        # print(lno)
        self.summary = Summary(lno, text)

        line = next(lines, '')
        self.refs = line.split('; ')

        line = next(lines, '')
        while line.startswith('-'):
            self.lines.append(Span.parse(line[2:]))
            line = next(lines, '')

        self.next_line = line

    def __str__(self):
        refs = '<small>' + ' : '.join(self.refs) + '</small>\n<br/>'
        data = '\n<br/>'.join([Span.render(line) for line in self.lines])
        return f'    <details>\n{self.summary}\n      <div class="full">{refs}{data}</div></details>'
        
class Summary:
    def __init__(self, lno, text):
        self.lno = lno
        text, eds = text.split(' % ')
        self.editions = [False] * len(editions)
        for ed in eds:
            self.editions[editions.index(ed)] = True
        self.spans = Span.parse(text)

    def __str__(self):
        lno = f'<span class="lno">{self.lno}</span>'
        data = Span.render(self.spans)
        
        classes = map(lambda x: 'not' if not x[1] else f'ed {x[0].lower()}', \
            zip(editions, self.editions))
        spans = map(lambda x: f'<span class="{x[1]}">{x[0]}</span>', \
                    zip(editions, classes))
        eds = f'<span class="eds">{''.join(spans)}</span>'
        
        return f'      <summary>{lno} {data}{eds}</summary>'

class Span:
    punc = string.punctuation.replace("'", "") + '—'
    split = re.compile(r'''(\[[^]]+\]) |
                           (\*[^*]+\*) |
                           (\{[^}]+\}) |
                           (\\[^\\]+\\) |
                           (/[^/]+/)''', re.X)
    @classmethod
    def parse(cls, text):
        text = re.sub(r'\s*--\s*', '—', text)
        text = text.replace('...', '…')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('&lt;', '&lt;<i>')
        text = text.replace('&gt;', '</i>&gt;')
        while '_' in text:
            text = text.replace('_', '<i>', 1)
            _ = text.index('_') # throw an exception for unbalanced '_'
            text = text.replace('_', '</i>')
        spans = [Span(s.strip()) for s in
                 filter(lambda x: x is not None and x.strip(), \
                        re.split(Span.split, text))]
        return spans

    @classmethod
    def render(cls, spans):
        html = str(spans.pop(0))
        for span in spans:
            fragment = str(span)
            if span.text[0] not in cls.punc and not html.endswith('</sup>'):
                html += ' '
            html += fragment
        return html
    
    def __init__(self, text):
        match text[0]:
            case '{':
                self.style = 'source'
            case '/':
                self.style = 'orig'
            case '\\':
                self.style = 'new'
            case '[':
                self.style = 'del'
            case '*':
                self.style = 'ins'                
            case _:
                self.style = None

        if self.style == None:
            self.text = text
        else:
            self.text = text[1:-1]

    def __str__(self):
        match self.style:
            case 'source':
                return f'<sup>{self.text}</sup>'
            case None:
                return self.text
            case _:
                return f'<span class="{self.style}">{self.text}</span>'
            
    def __repr__(self):
        match self.style:
            case 'source':
                return f'{{self.text}}'
            case 'orig':
                return f'/{self.text}/'
            case 'new':
                return f'\\{self.text}\\'
            case 'del':
                return f'[{self.text}]'
            case 'ins':
                return f'*{self.text}*'
            case _:
                return self.text

with open(sys.argv[1]) as file:
    lines = (line.strip() for line in file.readlines())

diffs = []
line = next(lines, '')
while line:
    diff = Diff(line, lines)
    diffs.append(diff)
    line = diff.next_line

page = f'''<!DOCTYPE html>
<html>
  <head>
    <style>
      sup {{ font-size: 0.7em; }}
      summary .del {{ opacity: 70%; }}
      .del {{ text-decoration-line: line-through; opacity: 50%; }}
      .ins {{ font-weight: bold; }}
      .eds {{ float: right; }}
      .not {{ visibility: hidden; }}
      .orig {{ background-color: #f7e1ea; }}
      .new {{ background-color: #e1f7f0; }}
      .lno {{
          display: inline-block;
          font-size: smaller;
          text-align: right;
          width: 3em;
          padding-right: 0.5em;
      }}
      .full {{ padding-left: 4.5em; }}
    </style>
  </head>
  <body>
{'\n'.join(map(str, diffs))}
  </body>
</html>'''

print(page)
    

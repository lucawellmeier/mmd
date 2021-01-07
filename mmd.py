import re
import markdown2



class Parser:
    def __init__(self, code):
        self.lines = code.splitlines()
        self.blocks = []
        self.pos = 0
        self.header_regex = re.compile(r'(#+)(.*)')
        self.begin_dir_regex = re.compile(
                r'([A-Z]+)(\[([a-z0-9-]+)\])?( (.*))?')
        self.identify_next_block()
    def identify_next_block(self):
        if self.pos == len(self.lines): return 
        line = self.lines[self.pos]
        if not line or line.isspace():
            self.pos += 1
            return self.identify_next_block()
        match = self.header_regex.fullmatch(line)
        if match:
            self.pos += 1
            self.add_header(match)
            return self.identify_next_block()
        match = self.begin_dir_regex.fullmatch(line)
        if match:
            self.pos += 1
            self.add_dir(match)
            return self.identify_next_block()
        self.add_paragraph()
        return self.identify_next_block()
    def add_block(self, type_='', id_='', name='', content=''):
        block = {'type': type_, 'id': id_, 'name': name, 'content': content}
        self.blocks.append(block)
    def add_header(self, match):
        self.add_block(type_=match.group(1), name=match.group(2).strip())
    def add_dir(self, match):
        content = ''
        if self.pos < len(self.lines):
            line = self.lines[self.pos]
            while line.startswith('>'):
                content += line[1:] + '\n'
                self.pos += 1
                if self.pos == len(self.lines):
                    break
                line = self.lines[self.pos]
        self.add_block(type_=match.group(1), 
            id_=match.group(3) if match.group(3) else '', 
            name=match.group(4).strip() if match.group(4) else '', 
            content=content.strip())
    def add_paragraph(self):
        content = ''
        line = self.lines[self.pos]
        while line and not line.isspace():
            content += line + '\n'
            self.pos += 1
            if self.pos == len(self.lines): break
            line = self.lines[self.pos]
        self.add_block(content=content.strip())



class SimpleNumberer:
    def __init__(self, numbered_headers, numbered_subblocks):
        self.numbered_headers = numbered_headers
        self.numbered_subblocks = numbered_subblocks
        self.counts = len(self.numbered_headers) * [0]
        self.subblock_count = 0
        self.last_level = 0
    def track(self, block):
        if block['type'] in self.numbered_headers:
            level = self.numbered_headers.index(block['type'])
            if level == 0:
                self.subblock_count = 0
            if level < self.last_level:
                for i in range(level + 1, len(self.counts)):
                    self.counts[i] = 0
            self.counts[level] += 1
            self.last_level = level
            return tuple(self.counts[:level+1])
        elif block['type'] in self.numbered_subblocks:
            self.subblock_count += 1
            return (self.counts[0], self.subblock_count)
        else:
            return ()



class RefFinder:
    def __init__(self, replacer):
        self.ref_replacer = replacer
        self.ref_regex = re.compile(r'<@([a-z0-9-]+)(|(.*))?>')
    def replace_in(self, block):
        match = self.ref_regex.search(block['content'])
        while match:
            a = match.span()[0]
            b = match.span()[1]
            ref = match.group(1)
            name = match.group(2)
            raw = block['content']
            replaced = raw[:a] + self.ref_replacer(ref,name) + raw[b:]
            block.update({'content': replaced})
            match = self.ref_regex.search(block['content'])



def parse(code, numberer=SimpleNumberer(numbered_headers=['##', '###'], 
        numbered_subblocks=['LEMMA', 'THEOREM', 'PROPOSITION', 'COROLLARY']), 
        ref_replacer=lambda blocks,ref,name : ''):
    blocks = Parser(code).blocks
    for block in blocks:
        block.update({'number': numberer.track(block)})
    ref_finder = RefFinder(lambda ref,name : ref_replacer(blocks,ref,name))
    for block in blocks:
        ref_finder.replace_in(block)
    return blocks



LATEX_DISPLAY_DELIMS = [ ('$$', '$$'), ('\\[', '\\]') ]
LATEX_INLINE_DELIMS = [ ('$', '$'), ('\\(', '\\)') ]
LATEX_DELIMS = LATEX_DISPLAY_DELIMS + LATEX_INLINE_DELIMS

class LatexSanitizer:
    def __init__(self):
        self.storage = []
    def sanitize(self, code):
        for pair in LATEX_DELIMS:
            code = self._sanitize_perpair(pair, code)
        return code
    def _sanitize_perpair(self, pair, code):
        l = pair[0]
        r = pair[1]
        while True:
            a = code.find(l)
            b = code.find(r, a + len(l))
            if a < 0 or b < 0:
                break
            else:
                c = '%%%' + str(len(self.storage)) + '%%%'
                self.storage.append(code[a:b + len(r)])
                code = ''.join([code[:a], c, code[b + len(r):]])
        return code
    def reinsert(self, code):
        for i in range(len(self.storage)):
            c = '%%%' + str(i) + '%%%'
            a = code.find(c)
            b = a + len(c)
            code = ''.join([code[:a], self.storage[i], code[b:]])
        return code

def block_content_to_html(block):
    sanitizer = LatexSanitizer()
    sanitized_md = sanitizer.sanitize(block['content'])
    sanitized_html = markdown2.markdown(sanitized_md)
    return sanitizer.reinsert(sanitized_html)



################################################################################



if __name__ == '__main__':
    import os
    import sys
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()

    def ref_replacer(blocks, ref, name):
        found = next((block for block in blocks if block['id'] == ref), [None])
        if found != None:
            name = found['type'].title() + ' ' + '.'.join([str(n) for n in found['number']])
            return '<a href="#{}">{}</a>'.format(ref,name)
        else:
            return '<strong style="color: red;">reference {} not found</strong>'.format(ref)
    blocks = parse(code, ref_replacer=ref_replacer)

    newfile = os.path.splitext(filename)[0] + '.html'
    with open(newfile, 'w') as f:
        f.write(
'''<html>
<head>
<meta charset="utf-8">
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
  },
  svg: {
    fontCache: 'global'
  }
};
</script>
<style>
  body {
    font-size: 14px;
    max-width: 672px;
    margin: 24px auto;
    padding: 0 8px;
  }
  .statement {
    border: 1px solid lightgrey;
    padding: 0 8px;
    padding-top: 8px;
  }
  .proof p:first-of-type {
    display: inline;
  }
  .proof p:last-child:after {
    content: " \\220e";
  }
</style>
</head>
<body>
''')
        toc_inserted = False
        for block in blocks:
            content = block_content_to_html(block)
            if block['type'] in ['LEMMA', 'THEOREM', 'PROPOSITION', 'COROLLARY']:
                html = '<p><div id="{}" class="statement">'.format(block['id'])
                num = ' ' + '.'.join([str(c) for c in block['number']]) if block['number'] else ''
                name = ' ({})'.format(block['name']) if block['name'] else ''
                html += '<strong>{}{}</strong>{}:'.format(block['type'].title(), num, name)
                html += content
                html += '</div></p>\n'
                f.write(html)
            elif block['type'] == 'PROOF':
                html = '<p><div class="proof"><strong>Proof.</strong> '
                html += content
                html += '</div>\n'
                f.write(html)
            elif re.fullmatch('#+', block['type']):
                lvl = len(block['type'])
                if not toc_inserted and lvl == 2:
                    toc_inserted = True
                    headers = [block for block in blocks if re.fullmatch('#+', block['type']) and 2 <= len(block['type']) and len(block['type']) <= 3]
                    for header in headers:
                        id_ = '_'.join([str(c) for c in header['number']])
                        num = '.'.join([str(c) for c in header['number']]) + '. '
                        title = num + header['name']
                        indent = (len(header['type']) - 1) * 8
                        f.write('<a href="#{}" style="margin-left: {}px">{}</a><br>\n'.format(id_, indent, title))
                    f.write('\n')
                id_ = '_'.join([str(c) for c in block['number']])
                num = '.'.join([str(c) for c in block['number']]) + '. ' if block['number'] else ''
                html = '<h{} id={}>{}{}</h{}>\n'.format(lvl, id_, num, block['name'], lvl)
                f.write(html)
            else:
                f.write(content + '\n')
        f.write(
'''</body>
</html>''')

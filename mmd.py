import re
import markdown2



class ParsingError(Exception): pass

def make_block(type_='', id_='', name='', content=''):
    return {'type': type_, 'id': id_, 'name': name, 'content': content }

class Parser:
    def __init__(self, code):
        self.lines = code.splitlines()
        self.blocks = []
        self.pos = 0
        self.header_regex = re.compile(r'(#+)(.*)')
        self.begin_dir_regex = re.compile(
                r'([A-Z]+)(\[([a-z0-9-]+)\])?(.*)')
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
    def add_header(self, match):
        self.blocks.append(make_block(type_=match.group(1), 
            name=match.group(2).strip()))
    def add_dir(self, match):
        content = ''
        line = self.lines[self.pos]
        while line.startswith('>'):
            content += line[1:] + '\n'
            self.pos += 1
            if self.pos == len(self.lines):
                break
            line = self.lines[self.pos]
        self.blocks.append(make_block(type_=match.group(1), 
            id_=match.group(3) if match.group(3) else '', 
            name=match.group(4).strip() if match.group(4) else '', 
            content=content))
    def add_paragraph(self):
        content = ''
        line = self.lines[self.pos]
        while line and not line.isspace():
            content += line + '\n'
            self.pos += 1
            if self.pos == len(self.lines): break
            line = self.lines[self.pos]
        if line and not line.isspace():
            self.blocks.append(make_block(content=content))

def parse(code):
    return Parser(code).blocks



LATEX_DISPLAY_DELIMS = [ ('$$', '$$'), ('\\[', '\\]') ]
LATEX_INLINE_DELIMS = [ ('$', '$'), ('\\(', '\\)') ]
LATEX_DELIMS = LATEX_DISPLAY_DELIMS + LATEX_INLINE_DELIMS

class LatexSanitizer:
    def __init__(self):
        self.subs_rep = 16
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
            b = code.find(r, a + 1)
            if a < 0 or b < 0:
                break
            else:
                c = self.subs_rep * str(len(self.storage))
                self.storage.append(code[a:b + len(r)])
                code = ''.join([code[:a], c, code[b + len(r):]])
        return code
    def reinsert(self, code):
        for i in range(len(self.storage)):
            c = self.subs_rep * str(i)
            a = code.find(c)
            b = a + self.subs_rep
            code = ''.join([code[:a], self.storage[i], code[b:]])
        return code

def block_content_to_html(block):
    sanitizer = LatexSanitizer()
    sanitized_md = sanitizer.sanitize(block['content'])
    sanitized_html = markdown2.markdown(sanitized_md)
    return sanitizer.reinsert(sanitized_html)

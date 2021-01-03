import re
import markdown2



DIRECTIVES = ['DEFN', 'LEMMA', 'PROP', 'THM', 'CORL', 'EXM', 'EXC', 'PROOF']

LATEX_DISPLAY_DELIMS = [ ('$$', '$$'), ('\\[', '\\]') ]
LATEX_INLINE_DELIMS = [ ('$', '$'), ('\\(', '\\)') ]
LATEX_DELIMS = LATEX_DISPLAY_DELIMS + LATEX_INLINE_DELIMS



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
                r'(' + r'|'.join(DIRECTIVES) + r')(\[([a-zA-Z0-9-]+)\])?(.*)')
        self.end_dir_regex = re.compile(r'.*END')
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
        matched_end = self.end_dir_regex.fullmatch(line)
        while not matched_end:
            content += line + '\n'
            self.pos += 1
            if self.pos == len(self.lines):
                raise ParsingError('no END statement')
            line = self.lines[self.pos]
            matched_end = self.end_dir_regex.fullmatch(line)
        content += line[:-3]
        self.blocks.append(make_block(type_=match.group(1), 
            id_=match.group(3) if match.group(3) else '', 
            name=match.group(4).strip() if match.group(4) else '', 
            content=content))
        self.pos += 1
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










'''
def _parse_arg_string(args):
    f = args.find('#')
    if f == -1:
        return args.strip(), []
    tags = [x.strip() for x in args[f:].split('#') if x.strip()]
    return args[:f].strip(), tags 

def parse_mmd(code):
    lines = code.split('\n')

    # parse structure directives
    found_dirs = []
    for i in range(len(lines)):
        if len(lines[i]) == 0:
            continue
        toks = lines[i].split(' ', 2)
        if toks[0] not in DIRS:
            if len(toks[0]) == 0:
                continue
            startsasno = toks[0][0].isdigit() or toks[0][0] in ['+', '-']
            if startsasno and toks[0][0:].isdigit():
                id_ = int(toks[0][0:])
                if len(toks) > 1 and toks[1] in DIRS:
                    args = toks[2] if len(toks) > 2 else '' 
                    found_dirs.append((i, toks[1], args, id_))
        else:
            arg_split = lines[i].split(' ', 1)
            args = arg_split[1] if len(arg_split) > 1 else ''
            found_dirs.append((i, toks[0], args, None))
    
    # assign code lines to directives
    parts = []
    for j in range(len(found_dirs)):
        start = found_dirs[j][0] + 1
        end = found_dirs[j + 1][0] if j + 1 < len(found_dirs) else len(lines)
        name, tags = _parse_arg_string(found_dirs[j][2])
        part = { 'type': found_dirs[j][1],
            'name': name, 'tags': tags,
            'text': '\n'.join(lines[start:end]),
            'id': found_dirs[j][3] }
        parts.append(part)

    return parts

def create_mmd_piece(id_, type_, name, text, tags):
    mmd = ''
    if id_ is not None:
        mmd += str(id_) + ' '
    mmd += type_
    if name:
        mmd += ' ' + name
    if tags:
        mmd += ' #' + ' #'.join(tags)
    mmd += '\n' + text
    return mmd

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
        # assuming the latex is correct......hehe
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

def mmdtext_to_html(mmdtext):
    sanitizer = LatexSanitizer()
    sanitizedmmd = sanitizer.sanitize(mmdtext)
    sanitizedhtml = markdown2.markdown(sanitizedmmd)
    return sanitizer.reinsert(sanitizedhtml)
'''

import re



class Parser:
    def __init__(self, config, code):
        self.lines = code.splitlines()
        self.blocks = []
        self.pos = 0
        self.header_regex = re.compile(r'(#+)(.*)')
        all_dirs_regex = '|'.join(config['all_directives'])
        self.begin_dir_regex = re.compile(
                r'({})(\[([a-z0-9-]+)\])?( (.*))?'.format(all_dirs_regex))
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
    def add_block(self, type_='', id_='', name='', content='', class_=''):
        markers = {}
        for cls in config['classes']:
            markers['is_' + cls] = type_ in config['classes'][cls]
        block = {'type': type_, 'id': id_, 'name': name, 
            'content': content, **markers}
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
    def __init__(self, config):
        self.numbered_headers = config['numbered_headers']
        self.numbered_subblocks = config['numbered_subblocks']
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



def parse(code, config, ref_replacer=lambda blocks,ref,name : ''):
    blocks = Parser(config, code).blocks
    numberer = SimpleNumberer(config)
    for block in blocks:
        block.update({'number': str(numberer.track(block))[1:-1]})
    ref_finder = RefFinder(lambda ref,name : ref_replacer(blocks,ref,name))
    for block in blocks:
        ref_finder.replace_in(block)
    return blocks



class LatexSanitizer:
    def __init__(self, config):
        self.latex_delims = config['latex_delimiters']
        self.rep_delim = config['latex_sanitize_delimiter']
        self.storage = []
    def sanitize(self, code):
        for pair in self.latex_delims:
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
                c = self.rep_delim + str(len(self.storage)) + self.rep_delim
                self.storage.append(code[a:b + len(r)])
                code = ''.join([code[:a], c, code[b + len(r):]])
        return code
    def reinsert(self, code):
        for i in range(len(self.storage)):
            c = self.rep_delim + str(i) + self.rep_delim
            a = code.find(c)
            b = a + len(c)
            code = ''.join([code[:a], self.storage[i], code[b:]])
        return code



################################################################################



if __name__ == '__main__':
    import os
    import sys
    import json
    import markdown2
    import chevron

    def block_content_to_html(block, config):
        sanitizer = LatexSanitizer(config)
        sanitized_md = sanitizer.sanitize(block['content'])
        sanitized_html = markdown2.markdown(sanitized_md)
        return sanitizer.reinsert(sanitized_html)

    config = json.loads(open('/home/luca/zettelkasten/config.json', 'r').read())
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
    blocks = parse(code, config, ref_replacer=ref_replacer)
    for block in blocks:
        block['content'] = block_content_to_html(block, config)

    args = {
        'template': '{{> index}}',
        'partials_path': config['templates_path'],
        'partials_ext': 'ms.html',
        'data': {
            'blocks': blocks,

            'length': lambda text,render: str(len(render(text))),
            'tuple_to_dotted': lambda text,render: '.'.join([x.strip() for x in render(text).split(',') if x]),
            'tuple_to_scored': lambda text,render: '_'.join([x.strip() for x in render(text).split(',') if x]),
            'titelize': lambda text,render: render(text).title()
        },
    }
    html = chevron.render(**args)
    newfile = os.path.splitext(filename)[0] + '.html'
    open(newfile, 'w').write(html)
        
    '''toc_inserted = False
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
                f.write(content + '\n')'''

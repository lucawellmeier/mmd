import re



class Parser:
    def __init__(self, config, code):
        self.classes = config['classes']
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
        for cls in self.classes:
            markers['is_' + cls] = type_ in self.classes[cls]
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
                content += line[2:] + '\n'
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



class Numberer:
    def __init__(self, config):
        self.counts = config['numbering']
        for first_level in self.counts:
            self._reset_tree(first_level)
    def track(self, block):
        for first_level in self.counts:
            counts = self._track_in_tree(first_level, [], block)
            if counts: return counts
        return []
    def _reset_tree(self, node):
        node.update({'count': 0})
        if 'children' in node:
            for child in node['children']:
                self._reset_tree(child)
    def _track_in_tree(self, node, counts, block):
        if block['type'] in node['types']:
            node['count'] += 1
            for child in node['children']:
                self._reset_tree(child)
            return counts + [node['count']]
        else:
            for child in node['children']:
                counts = self._track_in_tree(child, counts + [node['count']], block)
                if counts: return counts
        return []



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
    numberer = Numberer(config)
    for block in blocks:
        block.update({'number': str(numberer.track(block))[1:-1]})
    ref_finder = RefFinder(lambda ref,name : ref_replacer(blocks,ref,name))
    for block in blocks:
        ref_finder.replace_in(block)
    return blocks



class LatexSanitizer:
    def __init__(self, config):
        self.latex_delims = [(x['left'], x['right']) for x in config['latex_display_delims'] + config['latex_inline_delims']]
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

    def ref_replacer(blocks, ref, name):
        found = next((block for block in blocks if block['id'] == ref), [None])
        if found != None:
            name = found['type'].title() + ' ' + '.'.join([str(n) for n in found['number']])
            return '<a href="#{}">{}</a>'.format(ref,name)
        else:
            return '<strong style="color: red;">reference {} not found</strong>'.format(ref)

    config = json.loads(open('/home/luca/zettelkasten/config.json', 'r').read())
    filename = sys.argv[1]
    with open(filename, 'r') as f: code = f.read()
    blocks = parse(code, config, ref_replacer=ref_replacer)
    for block in blocks:
        block['content'] = block_content_to_html(block, config)
    args = {
        'template': '{{> index}}',
        'partials_path': config['templates_path'],
        'partials_ext': 'ms.html',
        'data': {
            'config': config,
            'blocks': blocks,
            'length': lambda text,render: str(len(render(text))),
            # TODO: rename to list because its not a tuple anymore
            'tuple_to_dotted': lambda text,render: '.'.join([x.strip() for x in render(text).split(',') if x]),
            'tuple_to_scored': lambda text,render: '_'.join([x.strip() for x in render(text).split(',') if x]),
            'titelize': lambda text,render: render(text).title(),
            'escape_backslashes': lambda text,render: render(text).replace('\\', '\\\\')
        },
    }
    html = chevron.render(**args)
    newfile = os.path.splitext(filename)[0] + '.html'
    open(newfile, 'w').write(html)

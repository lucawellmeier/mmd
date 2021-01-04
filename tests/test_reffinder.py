from mmd import RefFinder



def ref_replacer_1(ref, name):
    return '<a href="#{}">Hallo</a>'.format(ref)
testblocks1 = [{'content': '<@hallo>'}]
def test_1():
    finder = RefFinder(ref_replacer_1)
    finder.replace_in(testblocks1[0])
    assert testblocks1[0]['content'] == '<a href="#hallo">Hallo</a>'



testblocks2 = [{'content': '<@hallo>'},{'id':'hallo'}]
def ref_replacer_2(ref,name):
    found = next((x for x in testblocks2 if x['id'] == ref))
    return '<a href="#{}">{}</a>'.format(ref,found['name'])
def test_2():
    finder = RefFinder(ref_replacer_1)
    finder.replace_in(testblocks1[0])
    assert testblocks2[0]['content']



def ref_replacer_3(ref,name):
    return '<a href="#{}">{}</a>'.format(ref,name)
testblocks3 = [{'content': '<@hallo|Buono>'}]
def test_3():
    finder = RefFinder(ref_replacer_3)
    finder.replace_in(testblocks3[0])
    assert 'Buono' in testblocks3[0]['content']

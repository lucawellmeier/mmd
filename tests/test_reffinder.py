from mmd import RefFinder



def ref_replacer_1(ref, name):
    return '<a href="#{}">Hallo</a>'.format(ref)
testblocks1 = [{'content': '<@hallo>'}]
def test_1():
    finder = RefFinder(ref_replacer_1)
    finder.replace_in(testblocks1[0])
    assert testblocks1[0]['content'] == '<a href="#hallo">Hallo</a>'

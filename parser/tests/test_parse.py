from mmd import parse



testcode1 = '''
DEFN[3] subnormality

 END

LEMMA[id5] Schur's lemma
a  END

THM Schur's theorem
b END
'''
def test_1():
    blocks = parse(testcode1)
    assert len(blocks) == 3
    assert blocks[0]['type'] == 'DEFN'
    assert blocks[1]['id'] == 'id5'
    assert blocks[1]['content'] == 'a  '
    assert blocks[2]['type'] == 'THM'
    assert blocks[2]['id'] == ''



testcode2 = '''

# oh junge

PROOF     
Hallo Welt

\\begin{align*}
    \\text{verrückter Trick} = 5 \\cdot x
\\end{align*} END


'''
def test_2():
    blocks = parse(testcode2)
    assert len(blocks) == 2
    assert blocks[0]['type'] == '#' and blocks[1]['type'] == 'PROOF'
    assert blocks[1]['name'] == '' and blocks[1]['id'] == ''
    assert blocks[1]['content'].count('\n') == 4



testcode3 = '''
# Ciao monde
THM[1]
 END

PROP

hahaha END
LEMMA[2]
END
### Hallo welt
EXM
 END
'''
def test_3():
    blocks = parse(testcode3)
    assert len(blocks) == 6
    assert blocks[3]['type'] == 'LEMMA'
    assert blocks[4]['type'] == '###'
    assert blocks[5]['content'] == ' '

from mmd import parse



testcode1 = '''
DEFINITION[3] subnormality

LEMMA[id5] Schur's lemma
> Hallo

THEOREM Schur's theorem
>
>
>
> ciao
'''
def test_1():
    blocks = parse(testcode1)
    assert len(blocks) == 3
    assert blocks[0]['type'] == 'DEFINITION'
    assert blocks[1]['id'] == 'id5'
    assert blocks[1]['content'] == 'Hallo'
    assert blocks[2]['type'] == 'THEOREM'
    assert blocks[2]['id'] == ''



testcode2 = '''

# oh junge

PROOF     
> Hallo Welt
> 
> \\begin{align*}
>     \\text{verrückter Trick} = 5 \\cdot x
> \\end{align*}


'''
def test_2():
    blocks = parse(testcode2)
    assert len(blocks) == 2
    assert blocks[0]['type'] == '#' and blocks[1]['type'] == 'PROOF'
    assert blocks[1]['name'] == '' and blocks[1]['id'] == ''
    assert blocks[1]['content'].count('\n') == 4



testcode3 = '''
# Ciao monde
THEOREM[1]
>

PROPOSITION
>
>hahaha
LEMMA[2]
>
### Hallo welt
EXAMPLE
> 
'''
def test_3():
    blocks = parse(testcode3)
    assert len(blocks) == 6
    assert blocks[3]['type'] == 'LEMMA'
    assert blocks[4]['type'] == '###'
    assert blocks[5]['content'] == ''



testcode4 = r'''
# Review of basic measure theory

Let $(X,d)$ be a locally compact and separable metric space. 
A measure $\mu \colon X \to \mathbb{R}^p$ is a countably additive mapping, i.e. 
\[
    \mu(B) = \sum_{i \in \mathbb{N}} \mu(B_i)
\]
for a disjoint union $B = \bigsqcup_{i \in \mathbb{N}} B_i$.
'''
def test_4():
    blocks = parse(testcode4)
    assert len(blocks) == 2
    assert blocks[1]['content'].count('\n') == 5



testcode5 = r'''
THEOREM'''
def test_5():
    blocks = parse(testcode5)
    assert len(blocks) == 1



testcode6 = r'''
## Rectifiable sets

Throughout this section we consider $\mathbb{R}^d$ and an integer $1 \leq k \leq d$.

A set $E \subset \mathbb{R}^d$ is called **countably $k$-rectifiable** if there
exists a countable family $\{\Gamma_i\}_i$ of roto-transled graphs of Lipschitz functions 
$\phi_i \colon D_i \subset \mathbb{R}^k \to \mathbb{R}^{d-k}$ such that
\[ H^k\left(E \setminus \bigcup_i \Gamma_i \right) = 0. \]
'''
def test_6():
    blocks = parse(testcode6)
    assert len(blocks) == 3
    assert blocks[0]['type'] == '##'
    assert blocks[1]['type'] == ''
    assert blocks[2]['type'] == ''

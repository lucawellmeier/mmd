import json
from mmd import Numberer



config1 = '''
{"numbering": [
    {
        "types": ["##"], 
        "children": [
            { "types": ["###"], "children": [] },
            { "types": ["LEMMA", "THEOREM", "COROLLARY", "PROPOSITION"], "children": [] }
        ]
    }
]}
'''
def test_1_1():
    cfg = json.loads(config1)
    n = Numberer(cfg)
    assert n.counts[0]['count'] == 0
    assert n.counts[0]['children'][1]['count'] == 0
def test_1_2():
    cfg = json.loads(config1)
    n = Numberer(cfg)
    n.track({'type': '##'})
    assert n.counts[0]['count'] == 1 and n.counts[0]['children'][0]['count'] == 0
    n.track({'type': '###'})
    n.track({'type': '###'})
    assert n.counts[0]['count'] == 1 and n.counts[0]['children'][0]['count'] == 2
    n.track({'type': '##'})
    assert n.counts[0]['count'] == 2 and n.counts[0]['children'][0]['count'] == 0
def test_1_3():
    cfg = json.loads(config1)
    n = Numberer(cfg)
    n.track({'type': '##'})
    n.track({'type': '##'})
    n.track({'type': 'PROPOSITION'})
    n.track({'type': 'THEOREM'})
    assert n.counts[0]['children'][1]['count'] == 2
    n.track({'type': '###'})
    n.track({'type': '###'})
    n.track({'type': '##'})
    n.track({'type': 'PROPOSITION'})
    assert n.counts[0]['children'][1]['count'] == 1
def test_1_4():
    cfg = json.loads(config1)
    n = Numberer(cfg)
    assert [0,1] == n.track({'type': '###'})
    assert [0,1] == n.track({'type': 'COROLLARY'})
    assert [1] == n.track({'type': '##'})
    assert [1,1] == n.track({'type': 'PROPOSITION'})
    assert [1,2] == n.track({'type': 'THEOREM'})
    assert [1,1] == n.track({'type': '###'})
    assert [1,2] == n.track({'type': '###'})
    assert [2] == n.track({'type': '##'})
    assert [2,1] == n.track({'type': 'LEMMA'})
def test_1_5():
    cfg = json.loads(config1)
    n = Numberer(cfg)
    assert [] == n.track({'type': '#'})
    assert [] == n.track({'type': 'EXAMPLE'})
    assert [] == n.track({'type': ''})
    assert [1] == n.track({'type': '##'})
    assert [1,1] == n.track({'type': 'PROPOSITION'})
    assert [] == n.track({'type': 'EXAMPLE'})
    assert [1,2] == n.track({'type': 'THEOREM'})
    assert [] == n.track({'type': 'PROOF'})
    assert [1,1] == n.track({'type': '###'})
    assert [1,2] == n.track({'type': '###'})
    assert [2] == n.track({'type': '##'})
    assert [] == n.track({'type': '#'})
    assert [2,1] == n.track({'type': 'LEMMA'})



config2 = '''
{"numbering": [
    {
        "types": ["#"],
        "children": []
    },
    {
        "types": ["##"], 
        "children": [
            { "types": ["###"], "children": [] },
            { "types": ["LEMMA", "THEOREM", "COROLLARY", "PROPOSITION"], "children": [] }
        ]
    }
]}
'''
def test_2_1():
    cfg = json.loads(config2)
    n = Numberer(cfg)
    assert n.counts[0]['count'] == 0
    assert n.counts[1]['count'] == 0
    assert [1] == n.track({'type': '#'})
    assert [0,1] == n.track({'type': '###'})
def test_2_2():
    cfg = json.loads(config2)
    n = Numberer(cfg)
    assert [1] == n.track({'type': '##'})
    assert [1] == n.track({'type': '#'})
    assert [2] == n.track({'type': '#'})
    assert [2] == n.track({'type': '##'})
    assert [3] == n.track({'type': '#'})
    assert [4] == n.track({'type': '#'})
    assert [] == n.track({'type': 'PROOF'})
    assert [2,1] == n.track({'type': '###'})



config3 = '''
{"numbering": [{
    "types": ["#"],
    "children": [{
        "types": ["##"],
        "children": [{
            "types": ["###"],
            "children": [{
                "types": ["####"],
                "children": []
            }]
        }]
    }]
}]}
'''
def test_3_1():
    cfg = json.loads(config3)
    n = Numberer(cfg)
    assert [0,1] == n.track({'type': '##'})
    assert [1] == n.track({'type': '#'})
    assert [2] == n.track({'type': '#'})
    assert [2,1] == n.track({'type': '##'})
    assert [2,1,0,1] == n.track({'type': '####'})
    assert [2,1,1] == n.track({'type': '###'})
    assert [2,1,2] == n.track({'type': '###'})
    assert [3] == n.track({'type': '#'})
    assert [4] == n.track({'type': '#'})
    assert [4,0,0,1] == n.track({'type': '####'})

from dna.engine import load_traits, interpret
from dna.presentation import plain_result

TRAITS = {t['id']: t for t in load_traits()}

def test_caffeine_heterozygote_is_not_declared_slow():
    t = TRAITS['caffeine']
    r = {'status':'Marker observed','genotype':'AC','meaning':t['alleles']['AC']}
    v = plain_result(t, r, True)
    assert 'uncertain' in v['headline'].lower()
    assert 'cannot reliably' in v['meaning']

def test_personalized_headlines():
    cases = [('eye_color','GG','Lighter'),('earwax','TT','Dry'),('lactose','AG','digest'),('actn3','TT','lack')]
    for id_, genotype, word in cases:
        t=TRAITS[id_]
        r={'status':'Marker observed','genotype':genotype,'meaning':t['alleles'][genotype]}
        assert word.lower() in plain_result(t,r,True)['headline'].lower()

def test_exploratory_marker_does_not_invent_trait():
    t = next(t for t in load_traits() if not t.get('alleles') and t['category'] != 'Health Genetics')
    r = {'status':'Research marker observed','genotype':'AG','meaning':'raw marker'}
    assert 'No reliable personal prediction' in plain_result(t,r,True)['headline']

def test_no_call_not_negative():
    t=TRAITS['lactose']
    r=interpret(t,{})
    assert 'not found' in plain_result(t,r,True)['headline'].lower()
    assert 'not a negative' in plain_result(t,r,True)['meaning'].lower()

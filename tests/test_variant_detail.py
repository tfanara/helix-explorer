from dna.engine import load_traits, interpret
from dna.presentation import plain_result

def test_cftr_variant_details():
    t = next(t for t in load_traits() if t['id'] == 'cftr')
    assert t['variant_name'] == 'N1303K'
    r = interpret(t, {'rs80034486': {'chromosome':'7', 'position':117292931, 'genotype':'CG'}})
    assert r['status'] == 'Variant allele observed — unconfirmed'
    assert 'N1303K' in plain_result(t, r, True)['headline']

def test_cftr_mismatch_not_interpreted():
    t = next(t for t in load_traits() if t['id'] == 'cftr')
    r = interpret(t, {'rs80034486': {'chromosome':'7', 'position':1, 'genotype':'CG'}})
    assert r['status'] == 'Reference position mismatch'

def test_cftr_cc_not_full_negative():
    t = next(t for t in load_traits() if t['id'] == 'cftr')
    r = interpret(t, {'rs80034486': {'chromosome':'7', 'position':117292931, 'genotype':'CC'}})
    assert 'does not rule out' in r['meaning']

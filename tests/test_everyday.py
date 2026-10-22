from dna.presentation import everyday_result

def test_actn3_is_understandable_and_not_athletic_prediction():
    t = {'id': 'actn3'}
    meaning, caveat = everyday_result(t, {'status':'Marker observed', 'genotype':'TT'})
    assert 'muscles can still work normally' in meaning
    assert 'does NOT mean' in caveat

def test_unreviewed_variant_has_no_invented_prediction():
    meaning, caveat = everyday_result({'id':'unknown'}, {'status':'Marker observed', 'genotype':'AG'})
    assert 'does not support a reliable' in meaning

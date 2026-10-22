from dna.result_context import genotype_comparison, numeric_context

def test_eye_color_alternatives_and_current_genotype():
    rows = genotype_comparison({'id': 'eye_color'}, {'status':'Marker observed','genotype':'GG'})
    assert {r['Genotype'] for r in rows} == {'GG','AG','AA'}
    assert next(r for r in rows if r['Genotype']=='GG')['Your result'] == '✓ Yours'
    assert 'multi-marker' in numeric_context({'id':'eye_color'})

def test_no_speculative_health_genotype_comparison():
    assert genotype_comparison({'id':'cftr'}, {'status':'Variant allele observed — unconfirmed','genotype':'CG'}) == []

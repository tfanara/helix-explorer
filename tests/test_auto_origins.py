from dna.auto_origins import choose_markers, parse_batch, run_auto_comparison
import pytest


def fake_calls(n=80):
    return {f'rs{100000+i}': {'chromosome': str(1 + i % 20), 'position': 1_000_000 + (i // 20) * 7_000_000, 'genotype': 'AA'} for i in range(n)}


def mock_fetch(ids):
    return {rsid: {'mappings': [{'seq_region_name': fake_calls()[rsid]['chromosome'], 'start': fake_calls()[rsid]['position'], 'end': fake_calls()[rsid]['position'], 'assembly_name': 'GRCh37', 'strand': 1, 'allele_string': 'A/G'}], 'populations': [{'population': f'1000GENOMES:phase_3:{p}', 'allele': 'A', 'frequency': f} for p,f in [('GBR',.85),('FIN',.55),('YRI',.15)]]} for rsid in ids}


def test_auto_comparison_requires_no_reference_upload():
    result = run_auto_comparison(fake_calls(), fetcher=mock_fetch, minimum=30)
    assert result['markers'] >= 30
    assert 'British' in result['rows'][0]['Population']


def test_no_genotype_in_api_arguments():
    seen=[]
    def fetch(ids):
        seen.extend(ids)
        return mock_fetch(ids)
    run_auto_comparison(fake_calls(), fetcher=fetch)
    assert all(s.startswith('rs') for s in seen)


def test_mismatched_position_is_rejected():
    calls=fake_calls()
    data=mock_fetch(['rs100000'])
    data['rs100000']['mappings'][0]['start'] += 1
    assert parse_batch(data,calls,['rs100000']) == {}


def test_insufficient_reference_fails_closed():
    with pytest.raises(ValueError, match='no usable population data'):
        run_auto_comparison(fake_calls(), fetcher=lambda ids: {}, minimum=30)

import pytest
from dna.ancestry import parse_reference, compare_populations


def fixture_data(n=40):
    lines = ['rsid,chromosome,position,allele,population,frequency']
    calls = {}
    for i in range(n):
        rsid = f'rs{100000+i}'
        position = 2_000_000 + i * 2_000_000
        calls[rsid] = {'genotype': 'AA', 'chromosome': '1', 'position': position}
        for pop, freq in [('Pop1', .9), ('Pop2', .5), ('Pop3', .1)]:
            lines.append(f'{rsid},1,{position},A,{pop},{freq}')
    return calls, ('\n'.join(lines)).encode()


def test_comparison_uses_multiple_loci():
    calls, raw = fixture_data()
    result = compare_populations(calls, parse_reference(raw), bootstraps=20)
    assert result['markers'] == 40
    assert result['rows'][0]['Population'] == 'Pop1'
    assert result['rows'][0]['Relative log-likelihood'] == 0


def test_requires_sufficient_loci():
    calls, raw = fixture_data(20)
    with pytest.raises(ValueError, match='at least 30'):
        compare_populations(calls, parse_reference(raw))


def test_rejects_build_mismatch():
    calls, raw = fixture_data()
    calls['rs100000']['position'] += 1
    result = compare_populations(calls, parse_reference(raw))
    assert result['markers'] == 39
    assert result['rejected']['genome build / position mismatch'] == 1


def test_invalid_frequency():
    _, raw = fixture_data()
    with pytest.raises(ValueError, match='Invalid reference row'):
        parse_reference(raw.replace(b'Pop1,0.9', b'Pop1,1.5'))

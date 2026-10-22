from dna.highlights import build_highlights
from dna.geography import extract_frequencies

def test_geography_filters_correct_allele_and_reference_population():
    payload = {'populations': [
        {'population': '1000GENOMES:phase_3:GBR', 'allele': 'A', 'frequency': 0.2},
        {'population': '1000GENOMES:phase_3:GBR', 'allele': 'G', 'frequency': 0.8},
        {'population': 'OTHER:GBR', 'allele': 'A', 'frequency': 0.1},
        {'population': '1000GENOMES:phase_3:XYZ', 'allele': 'A', 'frequency': 0.3},
    ]}
    rows = extract_frequencies(payload, 'A')
    assert len(rows) == 1
    assert rows[0]['Allele frequency'] == .2

def test_highlights_excludes_generic_and_absent_cftr():
    traits = [
        {'id':'cftr','title':'CF','category':'Health Genetics','gene':'CFTR','rsid':'rs80034486','alleles':{'CC':'absent'}, 'expected_chromosome':'7','expected_position_grch37':117292931},
        {'id':'misc','title':'Research','category':'Appearance','gene':'ABC','rsid':'rs10','alleles':{}},
    ]
    calls = {'rs80034486':{'genotype':'CC','chromosome':'7','position':117292931}, 'rs10':{'genotype':'AG','chromosome':'1','position':10}}
    highlights, exploratory, missing = build_highlights(traits, calls)
    assert not highlights
    assert len(exploratory) == 2
    assert not missing

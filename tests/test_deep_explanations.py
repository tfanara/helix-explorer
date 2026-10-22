from dna.engine import load_traits
from dna.deep_explanations import DETAILS, detailed_explanation


def test_every_trait_has_three_useful_sections():
    traits = load_traits()
    assert len(traits) >= 59
    assert {t['id'] for t in traits} == set(DETAILS)
    for trait in traits:
        info = detailed_explanation(trait, {'genotype': '—', 'status': 'Not tested / no usable call'})
        for key in ('biology', 'importance', 'action', 'takeaway'):
            assert len(info[key]) > 35, (trait['id'], key)
        assert len(info['alternatives']) == len(trait.get('alleles', {}))


def test_research_marker_does_not_invent_a_personal_prediction():
    t = next(t for t in load_traits() if t['id'] == 'marker_rs1800795')
    result = detailed_explanation(t, {'genotype': 'AG', 'status': 'Research marker observed'})
    assert 'no reviewed' in result['takeaway']
    assert not result['alternatives']


def test_secretor_has_three_comparisons_and_real_world_context():
    t = next(t for t in load_traits() if t['id'] == 'fut2')
    result = detailed_explanation(t, {'genotype': 'AA', 'status': 'Marker observed', 'meaning': 'Nonsecretor'})
    assert len(result['alternatives']) == 3
    assert any(row['Your genotype'] == '✓ Yours' for row in result['alternatives'])
    assert 'norovirus' in result['importance'].lower()

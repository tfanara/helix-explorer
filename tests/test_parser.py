from dna.parser import parse_upload
from dna.engine import interpret, load_traits

SAMPLE=b'''# Example synthetic data\nrsid\tchromosome\tposition\tallele1\tallele2\nrs12913832\t15\t28365618\tG\tG\nrs80034486\t7\t117292931\tC\tG\nrs000000\t1\t123\t0\t0\n'''

def test_parser():
    calls, stats = parse_upload(SAMPLE, 'synthetic.txt')
    assert stats['records']==3
    assert stats['called']==2
    assert stats['no_call']==1
    assert calls['rs80034486']['genotype']=='CG'

def test_trait():
    calls,_ = parse_upload(SAMPLE,'synthetic.txt')
    trait = next(t for t in load_traits() if t['id']=='eye_color')
    assert 'lighter eyes' in interpret(trait,calls)['meaning']

def test_missing_not_negative():
    trait = next(t for t in load_traits() if t['id']=='cftr')
    assert interpret(trait,{})['status'].startswith('Not tested')

def test_expanded_catalog_unique_and_safe():
    traits=load_traits()
    assert len(traits)>=50
    assert len({t['rsid'] for t in traits})==len(traits)
    for trait in traits:
        assert trait['source'].startswith('https://')
        assert trait['category']
        assert trait['caveat']

def test_research_marker_no_prediction():
    trait=next(t for t in load_traits() if t['rsid']=='rs1805007')
    result=interpret(trait,{'rs1805007':{'genotype':'TT','chromosome':'16','position':89900000}})
    assert result['status']=='Research marker observed'
    assert 'no validated personalized' in result['meaning']

def test_cftr_mismatch_withheld():
    trait=next(t for t in load_traits() if t['id']=='cftr')
    result=interpret(trait,{'rs80034486':{'genotype':'CG','chromosome':'7','position':123}})
    assert result['status']=='Reference position mismatch'

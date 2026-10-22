import json
from pathlib import Path

CAT_ICONS = {'Appearance':'👁️', 'Food & Nutrition':'🥛', 'Fitness':'🏃', 'Immune & Infections':'🧬', 'Sleep & Behavior':'🌙', 'Health Genetics':'🩺'}

def load_traits():
    return json.loads((Path(__file__).resolve().parent.parent / 'data' / 'traits.json').read_text())

def interpret(trait, genotypes):
    call = genotypes.get(trait['rsid'])
    if not call:
        return {'status':'Not tested / no usable call', 'genotype':'—', 'meaning':'No usable genotype for this marker in the uploaded file. This is not a negative result.'}
    genotype = call['genotype']
    if trait.get('expected_chromosome') and (call['chromosome'] != trait['expected_chromosome'] or call['position'] != trait['expected_position_grch37']):
        return {'status':'Reference position mismatch', 'genotype':genotype, 'meaning':'The raw file location does not match the validated GRCh37 reference for this marker. Interpretation withheld.'}
    if trait['category'] == 'Health Genetics' and trait['id'] != 'cftr':
        return {'status':'Research marker observed', 'genotype':genotype, 'meaning':'Genotype observed. Clinical interpretation withheld; this is not a medical screening result.'}
    if not trait.get('alleles'):
        return {'status':'Research marker observed', 'genotype':genotype, 'meaning':'Genotype observed. This entry is for exploration only; no validated personalized trait prediction is configured.'}
    meaning = trait['alleles'].get(genotype)
    if meaning is None:
        return {'status':'Uninterpreted genotype', 'genotype':genotype, 'meaning':'Genotype observed, but no reviewed interpretation is configured for these alleles.'}
    return {'status':'Marker observed', 'genotype':genotype, 'meaning':meaning}

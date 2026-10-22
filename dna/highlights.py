"""Conservative, deterministic highlights. Not a disease-risk ranking."""
from dna.engine import interpret
from dna.presentation import plain_result

HIGHLIGHT_IDS = {'eye_color', 'skin', 'earwax', 'lactose', 'actn3', 'fut2', 'cftr'}
UNCERTAIN_IDS = {'caffeine', 'fto'}

def build_highlights(traits, calls):
    highlights, exploratory, unavailable = [], [], []
    for trait in traits:
        result = interpret(trait, calls)
        view = plain_result(trait, result, True)
        item = {'trait': trait, 'result': result, 'view': view}
        if result['status'] in ('Not tested / no usable call', 'Reference position mismatch', 'Uninterpreted genotype'):
            unavailable.append(item)
        elif trait['id'] in HIGHLIGHT_IDS and result['status'] in ('Marker observed', 'Variant allele observed — unconfirmed', 'Two variant alleles observed — unconfirmed'):
            highlights.append(item)
        elif trait['id'] in HIGHLIGHT_IDS and trait['id'] == 'cftr' and result['status'] == 'N1303K not observed at tested site':
            # Not a highlight: absence of one variant is not a negative carrier screen.
            exploratory.append(item)
        else:
            exploratory.append(item)
    highlights.sort(key=lambda x: (x['trait']['category'] == 'Health Genetics', x['trait']['title']))
    return highlights, exploratory, unavailable

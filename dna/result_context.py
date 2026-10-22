"""Transparent, genotype-aware educational comparisons; no fabricated probabilities."""
from dna.presentation import EVERYDAY_EXPLANATIONS, PERSONAL_HEADLINES


def genotype_comparison(trait, result):
    """Return reviewed genotype alternatives, with current call flagged."""
    if result.get('status') != 'Marker observed':
        return []
    trait_id = trait['id']
    if trait_id not in EVERYDAY_EXPLANATIONS:
        return []
    rows = []
    for genotype, (meaning, _) in EVERYDAY_EXPLANATIONS[trait_id].items():
        rows.append({
            'Genotype': genotype,
            'Typical association': PERSONAL_HEADLINES.get(trait_id, {}).get(genotype, meaning),
            'Your result': '✓ Yours' if result.get('genotype') == genotype else '',
        })
    return rows


def numeric_context(trait):
    """Explicitly distinguish association from validated conditional probability."""
    if trait['id'] == 'eye_color':
        return ('This is a strong association, particularly in studied European-ancestry groups. '
                'A defensible percentage chance of blue, green, or brown eyes requires a validated '
                'multi-marker prediction model and population-specific calibration; this single '
                'SNP does not supply one.')
    if trait['id'] == 'actn3':
        return ('This genotype can strongly predict whether the ACTN3 protein is made, '
                'but it cannot provide a reliable percentage chance of athletic success.')
    return ('No validated personal probability is available from this marker alone. '
            'A published allele frequency (how common a variant is) is not the same as '
            'the chance of experiencing a trait given your genotype.')

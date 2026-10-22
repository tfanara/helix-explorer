"""Educational variant-frequency presentation; never estimates an individual's ancestry."""
import re
from dna.geography import POPULATIONS


def genotype_alleles(genotype):
    value = str(genotype or '').upper().replace('/', '').replace('|', '').strip()
    if not re.fullmatch(r'[ACGT]{2}', value):
        return []
    return sorted(set(value))


def frequency_summary(rows):
    """Return sample-based allele frequency percentages, never personal trait odds."""
    clean = [r for r in rows if r.get('Code') in POPULATIONS and isinstance(r.get('Allele frequency'), (float, int)) and 0 <= r['Allele frequency'] <= 1]
    return sorted([{**r, 'Frequency (%)': round(100 * r['Allele frequency'], 1)} for r in clean], key=lambda r: r['Frequency (%)'], reverse=True)


def frequency_explanation(allele, genotype, rows):
    if not rows:
        return 'No comparable reference-population frequencies were returned for this allele.'
    return (f'These percentages show how often the **{allele} DNA letter** appears among sampled chromosomes in each reference population. '
            f'Your genotype is **{genotype}**, but the chart does not show the percentage of people with your exact two-letter genotype, '
            'the chance of having the trait, or the percentage of your ancestry from a place. '
            'Reference samples are limited and are not representative of everyone in a country.')

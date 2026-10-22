"""Exploratory multi-locus population frequency comparison; NOT ancestry estimation."""
import csv
import io
import math
import random
from collections import defaultdict

MIN_MARKERS = 30
MIN_POPULATIONS = 3
MAX_REFERENCE_BYTES = 5_000_000


def parse_reference(raw):
    """Reference CSV: rsid,chromosome,position,allele,population,frequency.

    Position is GRCh37 forward strand. Each population must have one frequency
    per biallelic SNP, for the SAME specified allele. Frequencies are observed
    reference-sample frequencies, not invented estimates.
    """
    if len(raw) > MAX_REFERENCE_BYTES:
        raise ValueError('Reference CSV exceeds 5 MB.')
    try:
        content = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('Reference CSV must be UTF-8.') from exc
    reader = csv.DictReader(io.StringIO(content))
    expected = {'rsid', 'chromosome', 'position', 'allele', 'population', 'frequency'}
    if not reader.fieldnames or not expected.issubset(set(reader.fieldnames)):
        raise ValueError('Missing required reference CSV columns: ' + ', '.join(sorted(expected)))
    loci = {}
    seen = set()
    for row in reader:
        rsid, chrom, allele, pop = (row[k].strip() for k in ('rsid', 'chromosome', 'allele', 'population'))
        try:
            position = int(row['position'])
            frequency = float(row['frequency'])
        except (TypeError, ValueError) as exc:
            raise ValueError('Invalid position or frequency.') from exc
        if not (rsid.startswith('rs') and rsid[2:].isdigit() and chrom in {str(i) for i in range(1, 23)} and position > 0 and allele in 'ACGT' and len(allele) == 1 and pop and math.isfinite(frequency) and 0 <= frequency <= 1):
            raise ValueError('Invalid reference row (autosomal, GRCh37, A/C/G/T allele, frequency 0–1 required).')
        key = (rsid, pop)
        if key in seen:
            raise ValueError('Duplicate rsID/population in reference CSV.')
        seen.add(key)
        entry = loci.setdefault(rsid, {'chromosome': chrom, 'position': position, 'allele': allele, 'frequencies': {}})
        if (entry['chromosome'], entry['position'], entry['allele']) != (chrom, position, allele):
            raise ValueError('Inconsistent location or reference allele for ' + rsid)
        entry['frequencies'][pop] = frequency
    return loci


def compare_populations(calls, reference, minimum=MIN_MARKERS, bootstraps=150):
    """Compare log genotype likelihoods, not ancestry percentages or admixture.

    Uses Hardy-Weinberg genotype probabilities and independent-locus assumption.
    Requires identical covered loci across all compared populations. To avoid
    correlated SNPs, retains at most one marker per 1 Mb genomic window.
    """
    populations = sorted(set.intersection(*(set(v['frequencies']) for v in reference.values()))) if reference else []
    if len(populations) < MIN_POPULATIONS:
        raise ValueError('Need at least three populations represented at every reference locus.')
    usable = []
    used_windows = set()
    rejected = defaultdict(int)
    for rsid, locus in sorted(reference.items(), key=lambda x: (int(x[1]['chromosome']), x[1]['position'])):
        call = calls.get(rsid)
        if not call:
            rejected['not present in DNA file'] += 1
            continue
        if (call['chromosome'], call['position']) != (locus['chromosome'], locus['position']):
            rejected['genome build / position mismatch'] += 1
            continue
        genotype = call['genotype']
        allele = locus['allele']
        if len(genotype) != 2 or any(base not in 'ACGT' for base in genotype):
            rejected['invalid genotype'] += 1
            continue
        # A frequency for one allele is only sufficient to model biallelic loci.
        # Reject genotypes with two distinct non-reference bases.
        if len(set(genotype) - {allele}) > 1:
            rejected['potential multiallelic genotype'] += 1
            continue
        window = (locus['chromosome'], locus['position'] // 1_000_000)
        if window in used_windows:
            rejected['linked / nearby marker excluded'] += 1
            continue
        used_windows.add(window)
        count = genotype.count(allele)
        usable.append((rsid, count, [locus['frequencies'][p] for p in populations]))
    if len(usable) < minimum:
        raise ValueError(f'Only {len(usable)} independent, position-matched markers are usable; at least {minimum} are required. Provide a larger, genome-wide reference panel.')

    def scores(items):
        totals = [0.0] * len(populations)
        for _, count, freqs in items:
            for i, f in enumerate(freqs):
                f = min(.999, max(.001, f))
                # Binomial coefficient cancels in population comparisons.
                totals[i] += count * math.log(f) + (2 - count) * math.log(1 - f)
        return totals

    totals = scores(usable)
    rng = random.Random(20261021)
    wins = [0] * len(populations)
    for _ in range(bootstraps):
        sample = [usable[rng.randrange(len(usable))] for _ in usable]
        ss = scores(sample)
        wins[max(range(len(populations)), key=lambda i: ss[i])] += 1
    best = max(totals)
    rows = sorted(({'Population': p, 'Relative log-likelihood': round(totals[i] - best, 2), 'Bootstrap top-rank frequency': round(wins[i] / bootstraps, 3)} for i, p in enumerate(populations)), key=lambda x: x['Relative log-likelihood'], reverse=True)
    return {'rows': rows, 'markers': len(usable), 'rejected': dict(rejected), 'population_count': len(populations)}

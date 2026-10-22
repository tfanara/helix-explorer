"""Automatic research comparison using Ensembl's public 1000 Genomes frequencies.

No genotype or DNA file is transmitted. Only publicly named rsIDs are queried.
Reference data is retrieved at runtime, not fabricated or shipped as fake data.
"""
import json
import math
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from dna.ancestry import compare_populations
from dna.geography import POPULATIONS

ENDPOINT = 'https://grch37.rest.ensembl.org/variation/homo_sapiens'
MAX_REQUEST_IDS = 40


def choose_markers(calls, max_markers=240):
    """Reproducible genome-wide sampling; at most one per 5 Mb window.

    These are NOT validated ancestry-informative SNPs; results are exploratory.
    """
    windows = {}
    for rsid, call in calls.items():
        chrom, pos, genotype = call.get('chromosome'), call.get('position'), call.get('genotype', '')
        if chrom not in {str(i) for i in range(1, 23)} or not isinstance(pos, int) or len(genotype) != 2 or any(c not in 'ACGT' for c in genotype):
            continue
        if not (rsid.startswith('rs') and rsid[2:].isdigit()):
            continue
        window = (int(chrom), pos // 5_000_000)
        if window not in windows or int(rsid[2:]) < int(windows[window][0][2:]):
            windows[window] = (rsid, call)
    # spread sampling evenly across chromosomes instead of using just chr1.
    by_chrom = {chrom: [] for chrom in range(1, 23)}
    for (chrom, window), (rsid, call) in sorted(windows.items()):
        by_chrom[chrom].append(rsid)
    result = []
    while len(result) < max_markers and any(by_chrom.values()):
        for chrom in range(1, 23):
            if by_chrom[chrom] and len(result) < max_markers:
                result.append(by_chrom[chrom].pop(0))
    return result


def parse_batch(payload, calls, requested):
    """Accept only biallelic, position-matched GRCh37 SNPs with complete population frequencies."""
    result = {}
    for rsid in requested:
        record = payload.get(rsid)
        call = calls.get(rsid)
        if not isinstance(record, dict) or not call:
            continue
        mappings = record.get('mappings') or []
        if not any(str(m.get('seq_region_name')) == call['chromosome'] and m.get('start') == call['position'] and m.get('end') == call['position'] and m.get('assembly_name', 'GRCh37') == 'GRCh37' and m.get('strand', 1) == 1 for m in mappings):
            continue
        alleles = record.get('MAF') # unused: use exact biallelic mapping below
        mapping = next((m for m in mappings if str(m.get('seq_region_name')) == call['chromosome'] and m.get('start') == call['position'] and m.get('end') == call['position']), None)
        allele_string = (mapping or {}).get('allele_string', '')
        pair = allele_string.split('/')
        if len(pair) != 2 or len(set(pair)) != 2 or any(len(a) != 1 or a not in 'ACGT' for a in pair):
            continue
        if any(base not in pair for base in call['genotype']):
            continue
        allele = sorted(pair)[0]
        freqs = {}
        for item in record.get('populations') or []:
            population = str(item.get('population', ''))
            code = population.rsplit(':', 1)[-1]
            if not population.startswith('1000GENOMES:phase_3:') or code not in POPULATIONS or item.get('allele') != allele:
                continue
            try:
                freq = float(item['frequency'])
            except (ValueError, TypeError, KeyError):
                continue
            if math.isfinite(freq) and 0 <= freq <= 1:
                freqs[code] = freq
        if len(freqs) >= 3:
            result[rsid] = {'chromosome': call['chromosome'], 'position': call['position'], 'allele': allele, 'frequencies': freqs}
    return result


def fetch_batch(rsids, timeout=20):
    data = json.dumps({'ids': rsids}).encode('utf-8')
    request = Request(ENDPOINT + '?pops=1', data=data, headers={
        'Content-Type': 'application/json', 'Accept': 'application/json',
        'User-Agent': 'HelixExplorerEducational/2.0'})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def run_auto_comparison(calls, fetcher=fetch_batch, max_markers=240, minimum=30):
    candidates = choose_markers(calls, max_markers)
    if len(candidates) < minimum:
        raise ValueError(f'Only {len(candidates)} suitable genome-wide markers found; need at least {minimum}.')
    collected = {}
    failed_batches = 0
    for i in range(0, len(candidates), MAX_REQUEST_IDS):
        batch = candidates[i:i + MAX_REQUEST_IDS]
        try:
            payload = fetcher(batch)
            if not isinstance(payload, dict):
                raise ValueError('Unexpected response from reference service')
            collected.update(parse_batch(payload, calls, batch))
        except (HTTPError, URLError, TimeoutError, ValueError, OSError):
            failed_batches += 1
    # Enforce a shared set of populations, not missing-as-zero frequencies.
    if not collected:
        raise ValueError('The public reference service returned no usable population data. Please try again later. No extra upload is required.')
    population_coverage = {}
    for record in collected.values():
        for pop in record['frequencies']:
            population_coverage[pop] = population_coverage.get(pop, 0) + 1
    selected = sorted((pop for pop, n in population_coverage.items() if n >= minimum))
    if len(selected) < 3:
        raise ValueError('Not enough reference populations have complete coverage for a reliable comparison. Try again later; no additional file is needed.')
    common = {rsid: dict(record, frequencies={pop: record['frequencies'][pop] for pop in selected})
              for rsid, record in collected.items() if all(pop in record['frequencies'] for pop in selected)}
    if len(common) < minimum:
        raise ValueError(f'Only {len(common)} comparable reference markers were available (minimum {minimum}). This public dataset cannot support a result for this upload right now; no second file is needed.')
    outcome = compare_populations(calls, common, minimum=minimum)
    outcome['reference_markers'] = len(common)
    outcome['requested_markers'] = len(candidates)
    outcome['failed_batches'] = failed_batches
    outcome['rows'] = [dict(row, Population=POPULATIONS[row['Population']][0]) for row in outcome['rows']]
    return outcome

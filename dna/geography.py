"""Fetch reference population allele frequencies by rsID only. Never transmit personal genotypes."""
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# 1000 Genomes Phase 3 reference population abbreviations, not ethnicity labels.
POPULATIONS = {
    'GBR': ('British in England and Scotland', 'Europe', 52.5, -1.5),
    'CEU': ('Utah residents with Northern/Western European ancestry', 'North America', 40.8, -111.9),
    'FIN': ('Finnish in Finland', 'Europe', 61.5, 25.7),
    'IBS': ('Iberian populations in Spain', 'Europe', 40.4, -3.7),
    'TSI': ('Toscani in Italy', 'Europe', 43.8, 11.3),
    'YRI': ('Yoruba in Ibadan, Nigeria', 'Africa', 7.4, 3.9),
    'LWK': ('Luhya in Webuye, Kenya', 'Africa', 0.6, 34.8),
    'GWD': ('Gambian in Western Division, The Gambia', 'Africa', 13.4, -16.6),
    'CHB': ('Han Chinese in Beijing', 'East Asia', 39.9, 116.4),
    'JPT': ('Japanese in Tokyo', 'East Asia', 35.7, 139.7),
    'BEB': ('Bengali in Bangladesh', 'South Asia', 23.8, 90.4),
    'GIH': ('Gujarati Indian in Houston, Texas', 'North America', 29.8, -95.4),
    'PJL': ('Punjabi in Lahore, Pakistan', 'South Asia', 31.5, 74.3),
    'PEL': ('Peruvians in Lima, Peru', 'South America', -12.0, -77.0),
    'MXL': ('Mexican ancestry in Los Angeles, California', 'North America', 34.1, -118.2),
    'CLM': ('Colombians in Medellin, Colombia', 'South America', 6.2, -75.6),
}

def extract_frequencies(payload, allele):
    rows = []
    for record in payload.get('populations', []):
        population = str(record.get('population', ''))
        code = population.rsplit(':', 1)[-1]
        if not population.startswith('1000GENOMES:phase_3:') or code not in POPULATIONS or str(record.get('allele', '')).upper() != allele.upper():
            continue
        try:
            freq = float(record['frequency'])
        except (KeyError, ValueError, TypeError):
            continue
        if not 0 <= freq <= 1:
            continue
        name, region, lat, lon = POPULATIONS[code]
        rows.append({'Population': name, 'Code': code, 'Region': region, 'Allele frequency': freq, 'Latitude': lat, 'Longitude': lon, 'Source': population})
    return sorted(rows, key=lambda r: r['Region'] + r['Population'])

def fetch_frequencies(rsid, allele, timeout=8):
    if not (rsid.startswith('rs') and rsid[2:].isdigit()):
        raise ValueError('Invalid rsID')
    if allele not in ('A', 'C', 'G', 'T'):
        raise ValueError('Select a single DNA letter')
    url = f'https://rest.ensembl.org/variation/human/{rsid}?pops=1'
    request = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'HelixExplorerEducational/1.0'})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except (URLError, HTTPError, TimeoutError, ValueError) as exc:
        raise RuntimeError('Population reference data could not be retrieved. Please try again later.') from exc
    return extract_frequencies(data, allele)

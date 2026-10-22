"""Fetch reference population allele frequencies by rsID only. Never transmit personal genotypes."""
import json
import time
import socket
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

class PopulationLookupError(RuntimeError):
    """An actionable, non-sensitive public reference lookup failure."""


def fetch_frequencies(rsid, allele, timeout=12, opener=urlopen, sleeper=time.sleep):
    """Query public Ensembl services with transient-error retries and clear diagnostics.

    Only an rsID is sent. Never send genotype, DNA contents, or user identifiers.
    """
    if not (isinstance(rsid, str) and rsid.startswith('rs') and rsid[2:].isdigit()):
        raise ValueError('Invalid rsID')
    allele = str(allele).upper()
    if allele not in ('A', 'C', 'G', 'T'):
        raise ValueError('Select a single DNA letter')

    endpoints = ('https://rest.ensembl.org', 'https://grch37.rest.ensembl.org')
    errors = []
    for host in endpoints:
        # Ensembl documents pops=1 and the JSON Content-Type header.
        url = f'{host}/variation/human/{rsid}?pops=1'
        for attempt in range(2):
            request = Request(url, headers={
                'Accept': 'application/json', 'Content-Type': 'application/json',
                'User-Agent': 'HelixExplorerEducational/2.1',
            })
            try:
                with opener(request, timeout=timeout) as response:
                    payload = json.load(response)
                if not isinstance(payload, dict):
                    raise ValueError('Invalid JSON response structure')
                if 'error' in payload:
                    raise ValueError('API error: ' + str(payload['error'])[:120])
                rows = extract_frequencies(payload, allele)
                if rows:
                    return rows
                # Successful response with no matching data is not a network outage.
                errors.append(f'{host}: no matching 1000 Genomes Phase 3 allele data')
                break
            except HTTPError as exc:
                errors.append(f'{host}: HTTP {exc.code}')
                if exc.code in (429, 500, 502, 503, 504) and attempt == 0:
                    sleeper(1)
                    continue
                break
            except (URLError, TimeoutError, socket.timeout, OSError) as exc:
                errors.append(f'{host}: connection/timeout ({type(exc).__name__})')
                if attempt == 0:
                    sleeper(1)
                    continue
                break
            except (ValueError, UnicodeError) as exc:
                errors.append(f'{host}: invalid response ({str(exc)[:90]})')
                break
    if errors and all('no matching' in e for e in errors):
        return []
    raise PopulationLookupError(
        'Could not load published population frequencies for ' + rsid + '. '
        + 'Details: ' + '; '.join(errors[-4:]) + '. '
        + 'Your genetic result is still valid as displayed; the geographic chart is temporarily unavailable.'
    )

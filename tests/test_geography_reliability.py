import io
import json
from urllib.error import HTTPError
import pytest
from dna.geography import fetch_frequencies, PopulationLookupError

class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

def payload():
    return {'populations': [{'population':'1000GENOMES:phase_3:GBR','allele':'G','frequency':0.62}]}

def test_success_and_request_parameters():
    seen = []
    def opener(req, timeout):
        seen.append(req)
        return Response(json.dumps(payload()).encode())
    result = fetch_frequencies('rs12913832', 'G', opener=opener)
    assert result[0]['Allele frequency'] == .62
    assert 'pops=1' in seen[0].full_url
    assert seen[0].get_header('Content-type') == 'application/json'

def test_retry_transient_failure():
    n = [0]
    def opener(req, timeout):
        n[0] += 1
        if n[0] == 1:
            raise HTTPError(req.full_url, 429, 'rate limit', {}, None)
        return Response(json.dumps(payload()).encode())
    assert fetch_frequencies('rs12913832', 'G', opener=opener, sleeper=lambda _: None)
    assert n[0] == 2

def test_no_frequency_is_not_service_failure():
    def opener(req, timeout): return Response(b'{"populations":[]}')
    assert fetch_frequencies('rs12913832', 'G', opener=opener) == []

def test_actionable_error():
    def opener(req, timeout): raise HTTPError(req.full_url, 403, 'forbidden', {}, None)
    with pytest.raises(PopulationLookupError, match='HTTP 403'):
        fetch_frequencies('rs12913832', 'G', opener=opener)

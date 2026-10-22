import io
import zipfile
import pytest
from dna.parser import parse_upload, MAX_BYTES

HEADER = b'rsid\tchromosome\tposition\tallele1\tallele2\n'

def test_normal_upload():
    calls, stats = parse_upload(HEADER + b'rs123\t1\t100\tA\tG\n', 'test.txt')
    assert calls['rs123']['genotype'] == 'AG'

def test_reject_large_raw():
    with pytest.raises(ValueError, match='35 MB'):
        parse_upload(b'X' * (MAX_BYTES + 1), 'test.txt')

def test_reject_zip_bomb_metadata():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('dna.txt', HEADER + b'#' * (MAX_BYTES + 100))
    with pytest.raises(ValueError, match='too large'):
        parse_upload(buf.getvalue(), 'dna.zip')

def test_reject_multiple_files():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('one.txt', HEADER)
        z.writestr('two.txt', HEADER)
    with pytest.raises(ValueError, match='exactly one'):
        parse_upload(buf.getvalue(), 'dna.zip')

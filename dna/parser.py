"""AncestryDNA-style TSV reader. No raw genotype files written to disk."""
from collections import Counter
import io
import zipfile

MAX_BYTES = 35 * 1024 * 1024
REQUIRED = ('rsid', 'chromosome', 'position', 'allele1', 'allele2')


def parse_upload(raw: bytes, filename: str):
    if len(raw) > MAX_BYTES:
        raise ValueError('File exceeds 35 MB upload limit.')
    if filename.lower().endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            members = [i for i in z.infolist() if not i.is_dir() and i.filename.lower().endswith(('.txt', '.tsv'))]
            if len(members) != 1:
                raise ValueError('ZIP must contain exactly one TXT/TSV DNA file.')
            if members[0].file_size > MAX_BYTES:
                raise ValueError('Uncompressed DNA file is too large.')
            raw = z.read(members[0])
    elif not filename.lower().endswith(('.txt', '.tsv')):
        raise ValueError('Upload a TXT, TSV or ZIP file.')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as e:
        raise ValueError('File must be UTF-8 text.') from e
    lines = (line for line in io.StringIO(text) if line.strip() and not line.startswith('#'))
    header = next(lines, '').strip().lower().split('\t')
    if tuple(header) != REQUIRED:
        raise ValueError('Expected AncestryDNA columns: rsid, chromosome, position, allele1, allele2.')
    genotypes = {}
    counts = Counter()
    for line_number, line in enumerate(lines, 2):
        cols = line.strip().split('\t')
        if len(cols) != 5:
            counts['malformed'] += 1
            continue
        rsid, chrom, pos, a, b = cols
        if not rsid.startswith('rs') or not pos.isdigit() or chrom not in {str(i) for i in range(1, 23)} | {'X','Y','MT','XY','26'}:
            counts['malformed'] += 1
            continue
        counts['records'] += 1
        if a == '0' or b == '0':
            counts['no_call'] += 1
            continue
        if a not in 'ACGT' or b not in 'ACGT':
            counts['special_encoding'] += 1
            continue
        if rsid in genotypes:
            counts['duplicate'] += 1
            continue
        genotypes[rsid] = {'genotype': ''.join(sorted((a,b))), 'chromosome': chrom, 'position': int(pos)}
        counts['called'] += 1
    if counts['records'] < 1:
        raise ValueError('No valid DNA rows found.')
    return genotypes, counts

"""Presentation helpers: bootstrap ranking is NOT ancestry composition."""
from dna.geography import POPULATIONS


def make_support_rows(rows):
    return [
        {'Population': row['Population'],
         'Top-rank consistency (%)': round(100 * row['Bootstrap top-rank frequency'], 1)}
        for row in rows
    ]


def make_map_rows(rows):
    by_name = {record[0]: (code, *record[1:]) for code, record in POPULATIONS.items()}
    points = []
    for row in rows:
        entry = by_name.get(row['Population'])
        if entry is None:
            continue
        code, region, lat, lon = entry
        support = max(0, min(1, row['Bootstrap top-rank frequency']))
        points.append({'Population': row['Population'], 'Region': region,
                       'lat': lat, 'lon': lon, 'marker_size': 2000 + 55000 * support,
                       'Top-rank consistency (%)': round(support * 100, 1)})
    return points

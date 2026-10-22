from dna.origins_view import make_map_rows, make_support_rows


def test_support_percent_is_not_admixture():
    rows = [{'Population': 'British in England and Scotland', 'Bootstrap top-rank frequency': .625}]
    assert make_support_rows(rows)[0]['Top-rank consistency (%)'] == 62.5


def test_map_has_grounded_coordinates_and_size():
    rows = [{'Population': 'British in England and Scotland', 'Bootstrap top-rank frequency': .6},
            {'Population': 'Finnish in Finland', 'Bootstrap top-rank frequency': .1}]
    mapped = make_map_rows(rows)
    assert len(mapped) == 2
    assert mapped[0]['marker_size'] > mapped[1]['marker_size']
    assert -90 <= mapped[0]['lat'] <= 90


def test_unknown_population_omitted_from_map():
    assert make_map_rows([{'Population': 'Unmapped', 'Bootstrap top-rank frequency': 1}]) == []

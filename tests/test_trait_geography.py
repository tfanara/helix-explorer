from dna.trait_geography import genotype_alleles, frequency_summary, frequency_explanation

def test_alleles_from_uploaded_genotype():
    assert genotype_alleles('GG') == ['G']
    assert genotype_alleles('GA') == ['A', 'G']
    assert genotype_alleles('--') == []
    assert genotype_alleles('G?') == []

def test_frequency_summary_does_not_invent_percentages():
    rows = [{'Code':'GBR','Population':'British','Allele frequency':0.34},
            {'Code':'FIN','Population':'Finnish','Allele frequency':0.75},
            {'Code':'XYZ','Population':'unknown','Allele frequency':0.99}]
    output = frequency_summary(rows)
    assert [r['Frequency (%)'] for r in output] == [75.0, 34.0]
    assert 'not' in frequency_explanation('G','GG',output)

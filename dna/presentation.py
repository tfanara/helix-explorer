"""Plain-language, conservative presentation of curated marker results."""

EXPLANATIONS = {
    'cftr': ('Cystic fibrosis carrier variant', 'CFTR helps control the movement of salt and water in cells. Some changes in this gene can cause cystic fibrosis when inherited from both parents.', 'Carrying one confirmed disease-causing CFTR variant usually does not mean you have cystic fibrosis. If both biological parents carry a disease-causing variant, each pregnancy has a 1-in-4 chance of an affected child.'),
    'apoe1': ('APOE and brain health', 'APOE helps move cholesterol and other fats through the body and brain.', 'Two markers, rs429358 and rs7412, are needed to identify common APOE types. This app does not calculate Alzheimer’s disease risk.'),
    'eye_color': ('Eye color tendency', 'This marker influences how much pigment is produced in the iris.', 'Other genes also affect eye color, so this is a tendency rather than a guarantee.'),
    'skin': ('Skin pigmentation tendency', 'This marker is associated with variation in skin pigment.', 'Many genes and sun exposure affect skin tone.'),
    'earwax': ('Earwax type', 'A variation in ABCC11 strongly influences whether earwax is wet or dry.', 'Your actual earwax type is easy to check directly.'),
    'lactose': ('Digesting milk as an adult', 'This region helps control whether the body keeps making lactase, the enzyme used to digest milk sugar.', 'Symptoms can differ, and other genetic variants can matter.'),
    'caffeine': ('How your body handles caffeine', 'CYP1A2 makes an enzyme that helps break down caffeine.', 'This one marker cannot tell you a safe caffeine dose or exactly how quickly you process coffee.'),
}

# Everyday-life explanations for markers with genotype-specific interpretations.
# The molecular finding is not automatically a prediction of a person's experience.
EVERYDAY_EXPLANATIONS = {
    'actn3': {
        'TT': ('Your muscles can still work normally. This common DNA pattern means your body probably does not make a particular protein found in fast-twitch muscle fibers. Other proteins help compensate.', 'It does NOT mean you are weak, cannot sprint, or are destined for endurance sports. Training and many other factors matter much more.'),
        'CC': ('Your DNA suggests you can make alpha-actinin-3, a protein used in some fast-twitch muscle fibers.', 'This does NOT mean you are naturally fast, strong, or a better athlete.'),
        'CT': ('Your DNA suggests you can make alpha-actinin-3, a protein used in some fast-twitch muscle fibers.', 'This does NOT mean you are naturally fast, strong, or a better athlete.'),
    },
    'eye_color': {
        'GG': ('This DNA pattern is associated with lighter eyes, especially blue, in some studied populations.', 'Eye color involves several genes; it is not a guarantee.'),
        'AG': ('You have one of each of two common DNA letters at an eye-pigment marker, so this single marker gives a mixed signal.', 'Your actual eye color depends on several other genes.'),
        'AA': ('This DNA pattern is associated with brown eyes in some studied populations.', 'Eye color involves several genes; it is not a guarantee.'),
    },
    'lactose': {
        'AA': ('Your DNA suggests your body is more likely to keep making lactase, the enzyme that digests milk sugar, after childhood.', 'This does not guarantee dairy will agree with you. Other causes of digestive symptoms exist.'),
        'AG': ('Your DNA suggests your body is more likely to keep making lactase, the enzyme that digests milk sugar, after childhood.', 'This does not guarantee dairy will agree with you. Other causes of digestive symptoms exist.'),
        'GG': ('This marker is associated with a greater chance of making less lactase as an adult in some populations.', 'Other variants can allow lactose digestion, and this result cannot diagnose lactose intolerance.'),
    },
    'earwax': {
        'TT': ('Your DNA suggests dry, flaky earwax is more likely.', 'This is a normal inherited difference, not a disease.'),
        'CT': ('Your DNA suggests wet or sticky earwax is more likely.', 'This is a normal inherited difference, not a disease.'),
        'CC': ('Your DNA suggests wet or sticky earwax is more likely.', 'This is a normal inherited difference, not a disease.'),
    },
    'caffeine': {
        'AA': ('Some research links this DNA pattern to higher activity of a caffeine-processing enzyme in certain circumstances.', 'It cannot tell you how long caffeine stays in your body or how much coffee is safe for you.'),
        'AC': ('You carry two different DNA letters at a caffeine-related marker. This alone cannot tell whether you process caffeine quickly or slowly.', 'Sleep, smoking, medicines, hormones, and other genes may matter more.'),
        'CC': ('Some research links this DNA pattern to lower activity of a caffeine-processing enzyme in certain circumstances.', 'It cannot tell you how long caffeine stays in your body or how much coffee is safe for you.'),
    },
    'fut2': {
        'AA': ('This genotype is associated with being a nonsecretor, meaning some blood-group-related sugars may be absent from certain body fluids.', 'It does not diagnose illness or reliably predict whether you will get infections.'),
        'AG': ('This genotype is associated with being a secretor, meaning certain blood-group-related sugars can appear in body fluids.', 'It does not diagnose illness or reliably predict whether you will get infections.'),
        'GG': ('This genotype is associated with being a secretor, meaning certain blood-group-related sugars can appear in body fluids.', 'It does not diagnose illness or reliably predict whether you will get infections.'),
    },
    'skin': {
        'AA': ('You have two copies of a DNA letter associated with lighter pigmentation in some populations.', 'Skin tone depends on many genes and cannot be determined from this one result.'),
        'AG': ('You have one copy of a DNA letter associated with lighter pigmentation in some populations.', 'Skin tone depends on many genes and cannot be determined from this one result.'),
        'GG': ('You do not carry the lighter-pigmentation-associated letter at this particular marker.', 'This does not determine your skin color or ancestry.'),
    },
}

def everyday_result(trait, result):
    """Return an accessible explanation without making unsupported predictions."""
    genotype = result.get('genotype', '')
    if result.get('status') not in ('Marker observed',):
        if trait['id'] == 'cftr' and 'observed' in result.get('status', '').lower():
            return ('Your raw DNA suggests a specific CFTR variant may be present. A clinical laboratory needs to confirm it.', 'Carrier status can matter when planning a pregnancy, but raw consumer DNA is not a medical test.')
        return ('There is not enough reliable information here to say how this gene affects you personally.', 'Finding a DNA marker does not automatically mean you have a noticeable trait.')
    return EVERYDAY_EXPLANATIONS.get(trait['id'], {}).get(genotype, (
        'This is a research marker, but your DNA result does not support a reliable everyday prediction.',
        'The gene may have a known biological role without telling us what you will experience.'
    ))

# Genotype-specific, reviewed educational headlines. The exact genotype is
# normalized by the parser and must match a reviewed allele mapping.
PERSONAL_HEADLINES = {
    'eye_color': {'GG': 'Lighter eyes are more likely', 'AG': 'This marker gives a mixed eye-color signal', 'AA': 'Brown eyes are more likely'},
    'skin': {'AA': 'A lighter-pigmentation allele is present twice', 'AG': 'One lighter-pigmentation allele is present', 'GG': 'This lighter-pigmentation allele was not observed'},
    'earwax': {'CC': 'Wet earwax is more likely', 'CT': 'Wet earwax is more likely', 'TT': 'Dry earwax is more likely'},
    'lactose': {'AA': 'You are more likely to digest lactose as an adult', 'AG': 'You are more likely to digest lactose as an adult', 'GG': 'Adult lactose digestion may be reduced'},
    'caffeine': {'AA': 'You may metabolize caffeine faster in some conditions', 'AC': 'Your caffeine-metabolism tendency is uncertain', 'CC': 'You may metabolize caffeine more slowly in some conditions'},
    'actn3': {'CC': 'You likely produce the ACTN3 muscle protein', 'CT': 'You likely produce the ACTN3 muscle protein', 'TT': 'You likely lack functional ACTN3 muscle protein'},
    'fto': {'AA': 'Two BMI-associated alleles observed', 'AT': 'One BMI-associated allele observed', 'TT': 'This BMI-associated allele was not observed'},
    'fut2': {'GG': 'You are likely a secretor', 'AG': 'You are likely a secretor', 'AA': 'You are likely a nonsecretor'},
}

# A/C is not a validated fast/slow caffeine classification. Avoid implying a
# known clearance rate or an individual caffeine recommendation.
CAFFEINE_MEANINGS = {
    'AA': 'This genotype has been associated with higher CYP1A2 inducibility in some studies. It does not measure your actual caffeine clearance rate.',
    'AC': 'You carry one A and one C allele. Research on this marker alone cannot reliably classify you as a fast or slow caffeine metabolizer. Some studies report intermediate patterns, but effects vary substantially.',
    'CC': 'This genotype has been associated with lower CYP1A2 inducibility in some studies. It does not measure your actual caffeine clearance rate.',
}

def plain_result(trait, result, uploaded):
    name, intro, context = EXPLANATIONS.get(trait['id'], (trait['title'], f"{trait['gene']} is a gene or region studied in connection with this topic.", 'This marker alone may not predict a noticeable personal trait.'))
    status = result['status']
    if not uploaded:
        headline = 'Upload your DNA file to see your result'
        meaning = 'You can learn about this gene now. Your personal result will appear after you upload a supported DNA file.'
    elif status == 'Reference position mismatch':
        headline = 'Result cannot be interpreted safely'
        meaning = 'The marker position does not match the expected reference. No personal conclusion is being made.'
    elif status == 'Not tested / no usable call':
        headline = 'This marker was not found in your file'
        meaning = 'This is not a negative test. Your DNA provider may not have tested this marker.'
    elif trait['id'] == 'cftr':
        if status == 'Variant allele observed — unconfirmed':
            headline = 'N1303K mutation: one copy detected in your raw DNA'
        elif status == 'Two variant alleles observed — unconfirmed':
            headline = 'N1303K mutation: two copies suggested by your raw DNA'
        elif status == 'N1303K not observed at tested site':
            headline = 'N1303K mutation not detected at this site'
        else:
            headline = 'N1303K: genotype found, interpretation unavailable'
        meaning = result['meaning']
    elif trait['category'] == 'Health Genetics':
        headline = 'Genetic marker found — no medical conclusion'
        meaning = 'Your file contains a genotype for this marker, but this app does not turn it into a diagnosis or disease-risk prediction.'
    elif status == 'Marker observed':
        genotype = result['genotype']
        headline = PERSONAL_HEADLINES.get(trait['id'], {}).get(genotype, 'Your genotype has a reviewed interpretation')
        meaning = CAFFEINE_MEANINGS.get(genotype, result['meaning']) if trait['id'] == 'caffeine' else result['meaning']
    else:
        headline = 'No reliable personal prediction from this marker'
        meaning = 'Your file contains this marker, but the scientific evidence is not sufficient for a meaningful individual prediction. The raw genotype remains available in DNA details.'
    return {'name': name, 'intro': intro, 'context': context, 'headline': headline, 'meaning': meaning, 'everyday': everyday_result(trait, result)}

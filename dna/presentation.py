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
        headline = 'CFTR variant data found — clinical confirmation required'
        meaning = 'A raw genotype is present at this location. The app cannot establish carrier status until the allele mapping and test quality have been clinically verified. If you have a clinical carrier result, rely on that result.'
    elif trait['id'] == 'apoe1' or (trait['category'] == 'Health Genetics'):
        headline = 'Genetic marker found — no medical conclusion'
        meaning = 'Your file contains a genotype for this marker, but this app does not turn it into a diagnosis or disease-risk prediction.'
    elif status == 'Marker observed':
        headline = 'Your DNA suggests a possible trait'
        meaning = result['meaning']
    else:
        headline = 'Your DNA contains this research marker'
        meaning = 'We found this marker in your file, but do not have a sufficiently reviewed personal prediction for it.'
    return {'name': name, 'intro': intro, 'context': context, 'headline': headline, 'meaning': meaning}

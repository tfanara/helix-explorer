"""Plain-language educational FAQ; no personal genotype data is used."""

FAQ = [
    ('DNA basics', 'What is DNA?', 'DNA is the instruction book inside almost every cell of your body. It contains information your cells use to grow, work, and repair themselves.'),
    ('DNA basics', 'What is a gene?', 'A gene is a stretch of DNA that helps your body make a useful product, often a protein. For example, CFTR provides instructions for a protein that moves salt across cell membranes.'),
    ('DNA basics', 'What is an allele?', 'An allele is a version of a genetic location. You usually inherit one copy from each biological parent. Imagine a spot in your DNA where some people have the letter C and others have G: C and G are two possible alleles at that spot.'),
    ('DNA basics', 'What is a genotype?', 'Your genotype is the pair of DNA letters reported at a particular location. For example, C/G means the file reports one C and one G. It does not, by itself, tell you whether either letter causes a health condition.'),
    ('DNA basics', 'What does heterozygous mean?', 'Heterozygous means your two copies differ at a location, such as C/G. It is not automatically good, bad, or disease-causing.'),
    ('DNA basics', 'What does homozygous mean?', 'Homozygous means your two copies match at a location, such as C/C or G/G. Whether that matters depends on the specific variant.'),
    ('DNA basics', 'What is a chromosome?', 'Chromosomes are long packages of DNA. Most people have 23 pairs. A raw DNA file often labels each marker with its chromosome and location.'),
    ('DNA basics', 'What is a SNP?', 'A SNP (pronounced “snip”) is a place in DNA where people commonly differ by one letter. A SNP is not necessarily harmful, and most are not useful for predicting a trait on their own.'),
    ('DNA basics', 'What is an rsID?', 'An rsID is a database label for a genetic variant, such as rs80034486. It is like a catalog number: it helps researchers find the same variant, but it is not a diagnosis.'),
    ('DNA basics', 'What is a genetic variant or mutation?', 'A variant is a DNA difference from a reference sequence. “Mutation” is sometimes used for a particular change, especially one associated with disease. Most variants are harmless or have uncertain effects.'),
    ('DNA basics', 'What is the difference between a gene and a mutation?', 'A gene is an entire section of DNA; a mutation is one particular change within it. CFTR is a gene, while N1303K is the name of a specific change in CFTR.'),
    ('Understanding results', 'What does C/G mean?', 'It means your uploaded file reports the DNA letters C and G at that location. The app must also know the correct reference build, DNA strand, and variant definition before assigning any biological meaning.'),
    ('Understanding results', 'What does N1303K mean?', 'N1303K is a short name for a CFTR protein change. At position 1303, the amino acid asparagine (N) is replaced by lysine (K). This variant is associated with cystic fibrosis. Finding a marker in consumer raw data is not the same as a confirmed clinical carrier result.'),
    ('Understanding results', 'What is a carrier?', 'A carrier has one disease-causing variant for a condition that typically requires two affected gene copies. Carriers are often healthy but can pass the variant to children. The meaning depends on the condition and should be confirmed clinically.'),
    ('Understanding results', 'If I am a cystic fibrosis carrier, will I have cystic fibrosis?', 'Usually, someone with one confirmed disease-causing CFTR variant does not have classic cystic fibrosis. A clinician can explain exceptions and reproductive implications based on a complete clinical test.'),
    ('Understanding results', 'What if both biological parents carry a CFTR variant?', 'When both parents carry disease-causing CFTR variants, each pregnancy generally has a 25% chance of a child with cystic fibrosis, a 50% chance of a carrier child, and a 25% chance of a child inheriting neither variant. A genetic counselor can provide individualized guidance.'),
    ('Understanding results', 'What does pathogenic mean?', 'Pathogenic means there is strong evidence that a variant can cause disease in an appropriate genetic context. It does not mean every person with that variant will be ill.'),
    ('Understanding results', 'What does uncertain significance mean?', 'A variant of uncertain significance (VUS) is one researchers cannot currently classify as harmless or disease-causing. It should not be used alone for medical decisions.'),
    ('Understanding results', 'What does “not tested” mean?', 'It means the uploaded file does not provide a usable result for that specific marker. It does NOT mean the variant is absent or that you are disease-free.'),
    ('Understanding results', 'Why do some results say “research only”?', 'Some reported associations come from studies of groups of people and do not reliably predict what will happen to one person. The app labels these as exploratory rather than presenting them as facts about you.'),
    ('Understanding results', 'What is a genome build or DNA strand?', 'A genome build is a version of the map used to number DNA positions. DNA has two complementary strands. If a file and reference use different maps or strands, letters and positions can be misread unless carefully matched.'),
    ('Understanding results', 'Why does the app show a gene but no prediction?', 'Knowing that a marker is present in your file is not enough to interpret it. Some traits depend on many genes; some variants need additional markers or clinical testing.'),
    ('Testing & accuracy', 'Does this app diagnose genetic diseases?', 'No. This is an educational explorer, not a diagnostic or comprehensive carrier-screening test. Discuss medically important findings with a qualified healthcare professional and confirm them through a clinical laboratory.'),
    ('Testing & accuracy', 'Can I trust raw AncestryDNA results for medical decisions?', 'Consumer genotyping files can contain errors, omit important variants, and use allele encodings that require verification. Do not change medical care, medication, or family-planning decisions based only on this app.'),
    ('Testing & accuracy', 'Why are some variants missing from my file?', 'Consumer DNA arrays measure selected locations, not your entire genome. A missing marker may simply not have been included in your test or may not have produced a usable call.'),
    ('Testing & accuracy', 'Does one gene determine a trait?', 'Sometimes one variant has a large effect, but most traits—like height, body weight, and athletic performance—depend on many genes plus environment and life experience.'),
    ('Testing & accuracy', 'Does a higher evidence rating guarantee my result?', 'No. Evidence strength describes how well a genetic association is supported, not whether a prediction is certain for one person.'),
    ('Privacy & uploads', 'Where does my uploaded DNA go?', 'In the hosted version, your browser sends the file to the Streamlit application server for processing. It is not processed exclusively in your browser. The app does not intentionally save raw DNA to a database or send it to an AI service.'),
    ('Privacy & uploads', 'Does “Clear my DNA” permanently erase everything?', 'It removes the app’s session references to your upload and parsed results, but cannot guarantee immediate erasure from server memory or control the hosting provider’s retention practices.'),
    ('Privacy & uploads', 'Can I upload a family member’s DNA?', 'Only upload another person’s DNA if you have appropriate permission. Genetic data is sensitive and can reveal information about biological relatives.'),
    ('Privacy & uploads', 'Can I download my results?', 'Yes. After uploading a supported file, you can export the curated marker results as a CSV. That CSV contains sensitive genotype data, so store and share it carefully.'),
]

CATEGORIES = list(dict.fromkeys(item[0] for item in FAQ))


def search_faq(category='All topics', query=''):
    """Filter by topic and plain-text search; no user genetic data involved."""
    q = query.casefold().strip()
    return [item for item in FAQ if (category == 'All topics' or item[0] == category)
            and (not q or q in (item[1] + ' ' + item[2]).casefold())]

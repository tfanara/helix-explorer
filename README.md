# Helix Explorer — local Streamlit MVP

**Educational/research prototype only. Not a medical device, diagnosis, comprehensive carrier test, or genetic counseling service.**

## macOS / Anaconda / VS Code

1. Download and unzip this project into a folder, e.g. `~/Documents/dna-explorer`.
2. Open **Terminal** and run:

```bash
cd ~/Documents/dna-explorer
conda create -n dna-explorer python=3.12 -y
conda activate dna-explorer
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

3. Open the local address printed in Terminal (usually `http://localhost:8501`).
4. In **VS Code**, choose **File → Open Folder** and open `dna-explorer`. Install the Microsoft Python extension if prompted. Open **Command Palette → Python: Select Interpreter** and choose the `dna-explorer` conda environment. Open a VS Code terminal, activate it if needed, and run `python -m streamlit run app.py`.
5. To stop, press **Ctrl+C** in the terminal. To restart later: `conda activate dna-explorer`, `cd` into the folder, and run `python -m streamlit run app.py`.

## Tests

```bash
python -m pytest -q
```

## What it does

- Accepts AncestryDNA-style TXT/TSV or ZIP containing one such file.
- Parses rsIDs and A/C/G/T calls, shows quality metrics, and explores curated categories.
- Offers trait details, source links, gene/variant search, exact rsID lookup, and CSV export.
- Does not intentionally persist uploads to disk or transmit genotype data to a third-party API.
- Keeps parsed genotypes in Streamlit server session memory until the session ends or is cleared.

## What it does NOT do

- Clinical carrier screening, diagnosis, drug dosing, full genetic risk scoring, ethnicity estimates, ancestry matching, or interpretation of unreviewed variants.
- Validate every possible genotype array, strand orientation, or insertion/deletion encoding.

## Public deployment warning

**Do not deploy this MVP for public DNA uploads without a privacy/security review.** Streamlit uploads are processed server-side, not exclusively in the user's browser. Plan secure session cleanup, privacy policy, threat modeling, source/version governance, audit of reference alleles, consent, logging restrictions, deletion procedures, and applicable regulatory/legal review. Do not commit any real DNA file to GitHub.

## Adding a trait

Add a carefully reviewed record to `data/traits.json`, including gene, rsID, reference allele interpretation, genome build, evidence and a source. Current records are an educational starter set, not a validated medical variant database. Add regression tests using **synthetic** data before release.

## Marker library expansion

This update increases the library to **59 marker entries** across six categories. New entries are deliberately **research-only marker lookups**: they show raw genotype presence but **do not infer a trait or medical finding** until the exact allele orientation, genome build, association strength, population applicability, and primary reference have been reviewed. Existing reviewed educational entries remain available. The CFTR N1303K interpretation also requires the expected GRCh37 chromosome/position.

For each new entry, the NCBI dbSNP link is an identification starting point, **not evidence that a phenotype prediction has been validated**. Do not convert research-only entries into medical or trait predictions without review and synthetic regression tests.

To update an existing installation, replace its `data/traits.json`, `dna/engine.py`, `tests/test_parser.py`, and `README.md` with the files from this release, or replace the entire project folder while preserving any personal changes separately.


## Publish this demo with Streamlit Community Cloud

## Public upload beta (updated)

The uploader is enabled with an explicit consent checkbox. There is no longer a `HELIX_ENABLE_DNA_UPLOADS` flag. The app processes DNA on the hosting server in session memory; this is **not** guaranteed zero-retention or medically validated. Do not broadly promote for real genetic data until a privacy/security/legal review. See `DEPLOY.md` for update instructions.

## Frequently asked questions

The **FAQ** tab is available even before a DNA upload. It includes searchable plain-English explanations of alleles, genes, genotypes, SNPs, mutations, carrier status, evidence, raw-data limitations, and privacy. Edit `dna/faq.py` to add or revise entries.

## Genotype-aware interpretations

The trait browser and gene search now use curated genotype-specific headlines for HERC2, SLC24A5, ABCC11, LCT/MCM6, CYP1A2, ACTN3, FTO and FUT2. CFTR N1303K retains its separate clinically cautious handling. Other research markers explicitly state that no reliable individual prediction is available. Caffeine A/C is **not** labeled as definitively fast or slow. These are educational associations, not validated health predictions.

## New in this release: Highlights and Genetic Geography

- **My Genetic Highlights** is the new landing page. It shows only curated, genotype-specific findings (and a separately labeled unconfirmed CFTR finding when applicable). It does not rank disease risk or treat absence of a variant as a health finding. Other exploratory and unavailable markers remain accessible.
- **Genetic Geography** retrieves allele frequencies for a selected rsID and DNA letter from the Ensembl variation REST API on demand. Only a public rsID is transmitted; uploaded DNA and genotypes are not sent to Ensembl. It plots reference sample locations (approximate) and frequencies; it does **not** infer ancestry percentages, ethnicity, nationality, or personal geographic origin.
- Population data require a working internet connection on the app server and are not guaranteed to be available for every variant/allele. Values are not precomputed or invented.


## Genetic origins and everyday descriptions
The highlights, trait browser and gene search now include everyday-language interpretations for selected reviewed genotypes. The geographic screen distinguishes the user's many SNPs from a validated ancestry analysis: **it does not claim to calculate geographic origin**. Its individual-marker frequency viewer remains educational. A real multi-marker model requires appropriately licensed population reference genotypes, QC, ancestry-informative SNP selection, allele harmonization, validation, and uncertainty estimates.

## Experimental multi-marker population comparison

The Origins page now includes a **real multi-locus reference-panel comparison engine** (`dna/ancestry.py`). It accepts an external, quality-controlled CSV with `rsid,chromosome,position,allele,population,frequency` columns, aligned to GRCh37 forward-strand calls. It requires at least 30 matching, widely spaced autosomal SNPs and three populations. It compares genotype log-likelihoods and reports reference-panel-relative rankings and marker-bootstrap stability, **not ancestry fractions or exposure history**. It does not provide a built-in reference panel: a vetted reference CSV is required. No reference frequencies are fabricated. Results are research-only and not calibrated as ancestry estimates. The file upload stays on the Streamlit host; no genotype is sent to Ensembl by this module.


## Single-upload genetic origins (experimental)
Upload AncestryDNA once. In Genetic Origins, click **Compare my DNA with reference populations**. The app automatically requests 1000 Genomes Phase 3 population frequencies from Ensembl GRCh37 using public rsIDs only. It does not upload personal genotypes or require a reference CSV. Internet access to Ensembl is required at analysis time; the public service may be slow, unavailable, or provide insufficient comparable SNPs, in which case the app shows no fabricated result. This is an exploratory, nonvalidated single-population fit, not ancestry fractions or geographic exposure.

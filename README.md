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

**Public DNA uploads are OFF by default.** This is a safe(r) educational demo, not a production genetics service. Users can browse the trait library without submitting DNA.

1. Create a GitHub repository (for example `helix-explorer`). Do not commit any actual DNA files.
2. Push this project's contents, keeping `app.py` and `requirements.txt` in the repository root.
3. Visit https://share.streamlit.io/ and choose **Create app** / **Deploy an app**, select your GitHub repository, branch `main`, and main file `app.py`.
4. Publish and test the educational browsing experience. Do not enable uploads on the public instance until an independent security/privacy and clinical-content review.
5. Local upload testing: run `HELIX_ENABLE_DNA_UPLOADS=true python -m streamlit run app.py` from your Mac Terminal.

### Privacy guardrail

The environment flag `HELIX_ENABLE_DNA_UPLOADS=true` bypasses the demo-only upload block. Do **not** configure this on a public Streamlit Community Cloud instance for real genetic files without reviewing data processing, retention, incident response, access controls, regulatory obligations, and explicit informed consent. Uploaded files and parsed genotypes can remain in Streamlit server memory during sessions. Publicly hosted processing is not local-only or zero-knowledge.

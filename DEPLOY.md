# Helix Explorer public upload beta

Uploads are enabled in this build; no environment variable is needed.

1. Run `python -m pytest -q` and inspect `git status` / `git diff` before committing.
2. Confirm no real DNA files or personal reports are in the repository **or Git history**.
3. Push the changed app and parser to your GitHub repo.
4. Streamlit Community Cloud should redeploy automatically. Check the app logs and verify the consent-gated uploader appears.
5. Test with a synthetic DNA file first, then check missing-variant states, clearing the session, and two separate browsers.
6. Before broadly promoting the service, obtain a security/privacy/legal review, add an appropriate privacy policy and contact, and assess provider retention, consent, and genetic-data regulations.

**Privacy limitations:** This is a public beta, not a verified zero-retention or medically validated platform. Streamlit uploads and parsed genotypes reside in hosting-server memory during sessions; a clear button cannot guarantee secure erasure from infrastructure. The app does not intentionally persist them to a database or send them to AI APIs.

## Updating an existing GitHub repo

Replace the current `app.py`, `dna/parser.py`, `DEPLOY.md`, and tests with the files from this package, then:

```bash
conda activate dna-explorer
cd ~/Documents/helix-explorer-deploy
python -m pip install -r requirements.txt
python -m pytest -q
git add app.py dna/parser.py DEPLOY.md tests/test_upload_safety.py
git commit -m "Enable consent-gated DNA uploads"
git push origin main
```

The new multi-marker comparison needs a vetted GRCh37 forward-strand population frequency CSV uploaded in the Origins page; it does not automatically infer ancestry without one. See README for the CSV schema and limitations.


No additional reference CSV upload is required. Genetic Origins uses the public Ensembl GRCh37 service on demand. Check availability on the hosted app; live requests were not tested in the offline build environment.

Trait cards now have optional on-demand reference-population maps. These need the hosted server to reach Ensembl; no additional user file upload is needed.

### Full explanation update
All 59 traits now include biology, everyday significance, and practical takeaways. Run `python -m pytest -q` before deployment.

# Helix Explorer deployment checklist

1. Confirm the repository contains **no real DNA files** (including commit history).
2. Run `python -m pytest -q`.
3. Commit and push to GitHub (`main`).
4. Deploy via https://share.streamlit.io/ with entry point `app.py`.
5. Keep `HELIX_ENABLE_DNA_UPLOADS` unset in the public deployment.
6. Verify users can browse the library but **cannot upload DNA**.
7. Verify no secrets or private files were committed.
8. Obtain privacy/security/clinical-content review before enabling personal DNA uploads.

Local development with uploads:

```bash
conda activate dna-explorer
cd ~/Documents/helix-explorer-deploy
HELIX_ENABLE_DNA_UPLOADS=true python -m streamlit run app.py
```

GitHub CLI example (requires prior `gh auth login`):

```bash
cd ~/Documents/helix-explorer-deploy
git init
git add .
git commit -m "Initial Helix Explorer public demo"
git branch -M main
gh repo create helix-explorer --public --source=. --remote=origin --push
```

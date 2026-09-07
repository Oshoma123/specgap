# Publish guide — GitHub (v0.1 pipeline release)

This repository was built in a sandbox with no outbound network access, so
the push has to happen from your own machine. This takes about 10 minutes.

**What you're publishing:** a tested, working pipeline (fetch → match → QA →
figures) validated on a synthetic fixture. The README and every document
already say plainly that the coverage numbers are not real yet. That's fine
to publish as-is — plenty of software gets its first release before its
first full dataset run — as long as nothing here is cited as a finding.

## 1. Unzip and check

Unzip `specgap.zip` into a working folder. Open `README.md` and confirm the
status line still reads "DRAFT v0.1 (unverified; pipeline validated only on
a synthetic fixture, not real data)" — don't change this until you've
actually run it on real data.

## 2. Create the repository

Go to [github.com/new](https://github.com/new). Suggested settings:
- **Repository name:** `specgap`
- **Description:** "Open engine for assessing the coverage of public MS/MS spectral libraries against natural-product structure databases"
- **Visibility:** Public (or Private if you'd rather keep it unlisted until real data is in)
- Leave it **empty** — no README, .gitignore, or license from GitHub's side (this repo already has all three)

Click **Create repository**. Don't close the next page — it shows the exact
remote URL you'll need in step 3.

## 3. Push from your machine

Open a terminal in the unzipped `specgap/` folder:

```bash
git init -b main
git add -A
git commit -m "SPECGAP v0.1: pipeline built and validated on synthetic fixture; real-data run pending"
git remote add origin https://github.com/<your-username>/specgap.git
git push -u origin main
```

Replace `<your-username>` with your actual GitHub username. If you use
SSH instead of HTTPS remotes, use `git@github.com:<your-username>/specgap.git`.

## 4. Tag the release

On GitHub: **Releases** tab → **"Draft a new release"** → tag `v0.1.0-draft`,
title "v0.1.0-draft — pipeline validated on synthetic fixture" → paste this
as the release notes:

> First public release of the SPECGAP pipeline: cross-matches natural-product
> structure databases (LOTUS, COCONUT) against open MS/MS spectral libraries
> (GNPS, MassBank, MoNA) on structural coverage and name-recoverability.
> Ships with a 12-test suite (unit + end-to-end) and CI, validated against a
> synthetic test fixture plus one real, verified COCONUT record — see
> README.md and docs/BUILD_SPEC.md. No real coverage findings are published
> yet.

→ **Publish release**.

## 5. Log it

Once pushed, copy the repo URL and add a row to your evidence log
(`docs/evidence_log_row_template.csv` has the format):

```
date, "SPECGAP v0.1.0-draft", software, GitHub, https://github.com/<you>/specgap, live, , pipeline validated on fixture, README.md screenshot, First public release; real-data run pending
```

## Later: Zenodo DOI

Not needed for this step. When you're ready for a citable DOI (ideally once
real data is in), the simplest path is: log in to [zenodo.org](https://zenodo.org)
with your ORCID, go to Account → GitHub, flip the switch for `specgap`, then
create a new GitHub release — Zenodo mints a DOI automatically within
minutes. `docs/PUBLISH_GUIDE.md` can be extended with the manual-upload path
too if you'd rather not link the accounts; just ask.

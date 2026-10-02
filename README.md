# FORM — workout intelligence on GitHub Pages

Python analytics with a black/blue HTML, CSS and JavaScript dashboard. Everything runs through GitHub Actions and GitHub Pages; no database, Supabase or Vercel account is required.

## Update workouts
Upload your app-export CSV into **source/**. Prefer replacing `source/workouts.csv` with a complete export; multiple exports are supported and matching set records are deduplicated. A commit on main automatically starts **Analyze workouts**. You can also choose **Actions → Analyze workouts → Run workflow**. The program tests the analysis, builds the report, preserves profile history and deploys the dashboard.

The supplied CSV is included as the initial source. This repository, source data and Pages dashboard are public per the requested configuration.

## Weight and height
Edit **[source/profile.txt](source/profile.txt)**:
```text
height_inches=69
weigh_in=2026-10-01,165,lb
weigh_in=2026-10-08,166,lb
```
Add a new line per weigh-in. Units can be `lb` or `kg`. Reusing a date changes that date's current entry. Changes trigger another build. Height 69 inches is 5′9″.

The program appends changed profile versions to **source/history/profile_history.json** and commits that history to main. Earlier values remain in the history and on the dashboard. Editing the profile again does not erase earlier archived versions. Git also retains previous committed source-file versions. Do not delete the history file if you want to keep the in-app archive.

Weight entries typed into the website are saved in **that browser's local storage**, not back to GitHub. Export a JSON backup, or add the entry to `source/profile.txt` for permanent repository storage and access on all devices. No GitHub credential is ever placed on the public site.

## Features
- Weekly sets, reps, logged volume, duration and workout frequency; inactive weeks shown as zero.
- Date filters, muscle distribution ring, schematic front/back muscle atlas with per-day filtering.
- Weekly direct set counters with a personal target.
- Exercise load, volume, repetitions and estimated strength trends; main exercise ranking.
- Data-quality reporting, muscle mapping overrides, and insights explaining the evidence and its limits.
- Weight logging, chart with 7-day rolling average, backup/restore, profile history and source height.

## Hosting
The **Analyze workouts** workflow deploys `web/` including freshly generated `report.json` and `profile.json`. It attempts to enable Pages automatically. If GitHub denies automatic enablement, set **Settings → Pages → Source: GitHub Actions**, then rerun the workflow.

## Run locally
```sh
python -m unittest discover -s tests -v
python analyzer/build_site.py
python -m http.server 8000 --directory web
```
Open http://localhost:8000.

## Interpretation
Direct sets exclude compound secondary muscle attribution. Muscle mapping is an editable heuristic in `source/muscle_overrides.json`. The atlas is a schematic. Estimated 1RM uses Epley on externally loaded sets of 1–12 reps; assisted and bodyweight work are excluded. Dumbbell export weights are not doubled. Compare loads on the same equipment. Trend comparisons use the first and last three eligible exercise sessions and require at least six. Insights describe associations, not proven causes; the export does not establish sleep, nutrition, recovery or technique. Insight windows are stated separately from chart filters. Planning targets are user-defined.

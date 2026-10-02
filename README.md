# FORM — private workout intelligence

Python analytics + responsive black/blue HTML/CSS/JavaScript dashboard. Built for the supplied workout-app CSV format. No paid AI API or Python packages required.

## What is included
- Weekly sets, repetitions, external-load volume, duration and workout frequency; zero-filled inactive weeks.
- Date filters, muscle distribution ring, schematic front/back muscle atlas with per-day filtering and keyboard-accessible muscle details.
- Weekly direct set counters with a personal planning target.
- Main exercises, load/volume/repetition charts and Epley estimated strength trends.
- Transparent muscle mapping overrides, duplicate detection, blank-row handling and data quality coverage.
- Logged-data insights with limitations instead of invented causal explanations.
- Weight entry, editing by date, deletion, trend chart, seven-day rolling average and JSON backup/restore.
- Local private mode and optional Supabase authenticated cloud report/weight storage with owner-only RLS.
- GitHub Actions analysis, tests and Pages deployment; Vercel static-hosting configuration.

## Privacy first
The repository was public at implementation time. **The personal export and generated report are deliberately not committed.** The public demo is synthetic.

Before uploading an export into `source/`, change repository **Settings → General → Danger Zone → Change repository visibility → Private**. Personal source files in a public git history are public even if the dashboard has a sign-in page. The analysis workflow refuses to process a public repository.

Ordinary GitHub Pages serves publicly accessible static files; a private repository does not automatically create a private Pages site. This deployment publishes only `web/` with fictional demo data. Actual reports are either loaded from a private Actions artifact locally or fetched through authenticated database row policies. If the entire website interface must be private, use protected hosting instead. Private repo Pages availability depends on your GitHub plan; enterprise private Pages requires applicable organization settings.

## Run your actual export
1. Make the repository private.
2. Upload your CSV into `source/` (one complete export recommended).
3. **Actions → Analyze workouts → Run workflow**, leave publish unchecked for local mode.
4. Download the `private-workout-report` artifact after success, unzip `report.json`.
5. Open the dashboard and choose **Load report JSON**. It is processed in your browser without upload.
6. Log weight on that device and export backups regularly. Local weight storage is not encrypted and is accessible to people using the same browser profile. Clearing browser storage removes it. The private report is held only in page memory.

Local development:
```sh
python analyzer/analyze.py --source source
python -m unittest discover -s tests -v
python -m http.server 8000 --directory web
```
Open `http://localhost:8000`. Click **Explore demo** for fictional training data. Upload real reports only in local mode or configured authenticated mode.

## GitHub Pages
Set **Settings → Pages → Build and deployment → Source: GitHub Actions**. Run **Deploy dashboard interface**. Pages publishes `web/` only; never move source CSVs or private report JSONs into `web/`.

## Optional cloud sync
A dedicated Supabase project could not be provisioned because the connected account has reached its two-active-free-project limit. Existing databases were left unchanged. No new cloud backend or alternate provider has been provisioned.

When a dedicated project is available:
1. Run `database.sql` in its SQL editor. Verify anon cannot read either table and two distinct users cannot access each other's rows.
2. Create your owner account via the Supabase Auth dashboard (email/password); disable public signup for a single-user app. Copy the owner's user UUID.
3. Set the public project URL and publishable key in `web/config.js`. **Never put service-role keys in frontend files.**
4. Add repository Actions secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `WORKOUT_OWNER_ID`.
5. Run Analyze workouts with publish enabled. Only the owner can select their report; weight writes are scoped to the signed-in user.
6. Sign in on the dashboard. Weights sync to the account. Import/restore local weight backups is currently supported in local mode only.

An alternative free database needs both secure authentication and an API; replacing just the storage connection is insufficient. The adapter is intentionally isolated in `analyzer/analyze.py` (`publish`) and `web/app.js` (cloud loading/weight persistence).

## Vercel
`vercel.json` configures only `web/` as the static output. Import this GitHub repository into Vercel, select Other framework, no build command, output directory `web`. Keep deployment protection enabled if the whole interface must be restricted. Never deploy the workspace root or `private-output/`. Live Vercel deployment was not completed.

## Interpretation
Primary-muscle assignment is a heuristic and can be overridden in `source/muscle_overrides.json`. Atlas is a schematic, not a medical/anatomical measurement. Direct sets exclude compound secondary muscle attribution; effort cannot be inferred when RPE is absent. Estimated 1RM uses externally loaded sets with 1–12 reps, excludes assistance and bodyweight work. Machine loads are comparable only within the same exercise/equipment. Dumbbell export weights are not doubled. Trends use the first and most recent three eligible exercise sessions and require at least six. Insights use the latest 28 logged-calendar days, while chart filters affect visible workload/exercise history; insight windows are explicitly stated. Nutrition, sleep and technique are not established from the export. Planning targets are user-defined.

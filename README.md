# job-radar

A personal daily job scanner. Runs once a day for free on GitHub Actions,
scores every posting against a weighted keyword profile you control, and
publishes the results to a dashboard you check whenever you like — no email,
no noise, no API key or billing setup required.

## How it works

1. **Search** — queries the [Adzuna](https://developer.adzuna.com/) job API
   (free tier, legitimate, no scraping) across Germany and Switzerland using
   the keywords in `config.yaml`, and separately checks specific companies'
   public Greenhouse job boards (e.g. MOIA).
2. **Score** — matches each posting's title and description against the
   weighted keywords you define in `config.yaml` (e.g. "Product Security
   Manager": 10). A title match counts at full weight; a description-only
   match counts at 40%. Fully transparent and free — no external API call.
3. **Store** — keeps everything above your `min_score` threshold in
   `docs/jobs.json`, tracking which postings are new since the last run.
4. **Publish** — GitHub Pages serves `docs/index.html`, a dashboard that
   reads that file directly. Bookmark the Pages URL and check it each morning.

## One-time setup (about 10 minutes)

### 1. Get free Adzuna API credentials
Sign up at https://developer.adzuna.com/ — instant, free, no credit card.
You'll get an `APP_ID` and `APP_KEY`.

### 2. Push this repo to GitHub
```bash
cd job-radar
git add -A
git commit -m "Initial job-radar setup"
git branch -M main
git remote add origin https://github.com/<your-username>/job-radar.git
git push -u origin main
```

### 3. Add your secrets
In your new GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**
Add both:
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`

### 4. Enable GitHub Pages
**Settings → Pages → Source: Deploy from a branch → Branch: `main` → Folder: `/docs`**
Save. GitHub will give you a URL like `https://<your-username>.github.io/job-radar/`
— that's your dashboard. Bookmark it.

### 5. Run it once manually to check everything works
**Actions tab → Daily job scan → Run workflow** (the button appears because
of the `workflow_dispatch` trigger in the workflow file). Watch the logs;
if the Adzuna call fails, the error will say exactly what's missing.

After that, it runs automatically every day at 06:00 UTC and commits the
updated `jobs.json` — your dashboard updates itself.

## Tuning it over time

Everything you'll want to change lives in `config.yaml`:
- **`profile.keyword_weights`** — the heart of the scoring. Add new terms as
  your positioning shifts (e.g. a new certification, a new target title),
  remove ones that aren't working, or adjust weights (10 = dream match,
  3-5 = nice-to-have). A title match counts full weight; a description-only
  match counts 40%, so heavily-weighted terms matter most when they appear
  in the job title itself.
- **`profile.min_score`** — raise it if you're getting too many low-quality
  matches, lower it if the board feels empty. Since scoring is just keyword
  math (not an LLM judgment call), it's worth checking a few jobs just below
  your threshold occasionally — a good match with unusual phrasing can score
  lower than it should.
- **`search.keywords`** — add/remove role titles as your search evolves.
- **`greenhouse_companies`** — add any company slug you want to watch
  directly (find the slug from their careers URL, e.g. `.../boards/moia/...`
  → slug is `moia`). Only works for companies using Greenhouse's public board.

## Extending later
- **Add more sources**: drop a new file in `scanner/sources/` following the
  same pattern as `adzuna.py` (return a list of dicts with the same keys),
  then call it from `main.py`.
- **Add email/Telegram notifications**: you chose dashboard-only for now,
  but the workflow step in `daily-scan.yml` is a natural place to add a
  "send if new_today > 0" step later — ask Claude when you're ready.
- **StepStone / XING**: neither offers a free public API like Adzuna or
  Greenhouse. If you want them back, the honest options are (a) their
  official recruiter-side APIs (paid, employer-facing, not really built for
  this), or (b) scraping, which is fragile and against their ToS — not
  recommended for a tool you want to run unattended every day.

## Local test run (optional)
```bash
pip install -r requirements.txt
export ADZUNA_APP_ID=xxx
export ADZUNA_APP_KEY=xxx
python main.py
```
Then open `docs/index.html` directly in a browser (or run `python -m http.server`
from inside `docs/` and visit `http://localhost:8000`).

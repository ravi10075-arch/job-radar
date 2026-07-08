"""
Persists job data to docs/jobs.json (the file the GitHub Pages dashboard reads).
Handles de-duplication across runs and tracks when each job was first seen,
so the dashboard can show "new today" vs. "seen before".
"""
import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
JOBS_FILE = ROOT / "docs" / "jobs.json"


def load_existing() -> dict:
    if not JOBS_FILE.exists():
        return {}
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {job["id"]: job for job in data.get("jobs", [])}


def merge_and_save(new_jobs: list[dict]) -> dict:
    today = datetime.date.today().isoformat()
    existing = load_existing()

    merged = dict(existing)  # start from what we had
    new_today_count = 0

    for job in new_jobs:
        job_id = job["id"]
        if job_id in existing:
            # Keep original first_seen, refresh everything else in case it changed
            job["first_seen"] = existing[job_id].get("first_seen", today)
            job["is_new"] = False
        else:
            job["first_seen"] = today
            job["is_new"] = True
            new_today_count += 1
        merged[job_id] = job

    output = {
        "last_run": datetime.datetime.utcnow().isoformat() + "Z",
        "total_jobs": len(merged),
        "new_today": new_today_count,
        "jobs": sorted(
            merged.values(),
            key=lambda j: (j.get("first_seen", ""), j.get("match_score", 0)),
            reverse=True,
        ),
    }

    JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output

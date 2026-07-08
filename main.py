"""
job-radar: daily scan entry point.

Run manually with:  python main.py
Run automatically via .github/workflows/daily-scan.yml (once a day, free).

Required environment variables (set as GitHub Actions secrets, or export
locally for a manual run):
  ADZUNA_APP_ID
  ADZUNA_APP_KEY

Scoring is rule-based (see scanner/scorer.py) - no API key or billing needed.
"""
import sys

from scanner.config import load_config
from scanner.sources import adzuna, greenhouse
from scanner.scorer import score_all
from scanner.store import merge_and_save


def collect_jobs(cfg: dict) -> list[dict]:
    jobs = []

    # --- Adzuna: broad keyword search across DE + CH ---
    for keyword in cfg["search"]["keywords"]:
        for country in cfg["search"]["countries"]:
            try:
                results = adzuna.fetch_jobs(
                    keyword, country, cfg["search"].get("results_per_query", 20)
                )
                jobs.extend(results)
                print(f"[adzuna] '{keyword}' in {country}: {len(results)} results")
            except Exception as e:
                print(f"[adzuna] ERROR for '{keyword}' in {country}: {e}", file=sys.stderr)

    # --- Greenhouse: specific companies you're watching directly ---
    for slug in cfg.get("greenhouse_companies", []):
        try:
            results = greenhouse.fetch_jobs(slug)
            jobs.extend(results)
            print(f"[greenhouse] {slug}: {len(results)} results")
        except Exception as e:
            print(f"[greenhouse] ERROR for '{slug}': {e}", file=sys.stderr)

    # De-dupe by URL within this run (same job can surface from multiple keywords)
    seen_urls = set()
    deduped = []
    for job in jobs:
        if job["url"] and job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            deduped.append(job)

    return deduped


def main():
    cfg = load_config()

    print("Collecting jobs...")
    jobs = collect_jobs(cfg)
    print(f"Collected {len(jobs)} unique postings before scoring.")

    print("Scoring jobs against weighted keyword profile...")
    scored = score_all(jobs, cfg["profile"]["keyword_weights"])

    min_score = cfg["profile"].get("min_score", 55)
    kept = [j for j in scored if j["match_score"] >= min_score]
    print(f"Kept {len(kept)} postings scoring >= {min_score}.")

    result = merge_and_save(kept)
    print(f"Saved. Total tracked jobs: {result['total_jobs']}, new today: {result['new_today']}")


if __name__ == "__main__":
    main()

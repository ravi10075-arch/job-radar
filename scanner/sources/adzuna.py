"""
Adzuna job search adapter.

Adzuna is a real, free-tier job search API (no scraping, no ToS risk).
Sign up for free credentials at https://developer.adzuna.com/
You get an APP_ID and APP_KEY - store these as GitHub Actions secrets
(ADZUNA_APP_ID / ADZUNA_APP_KEY), never commit them to the repo.

Free tier: 250 calls/month, 1000 results/call max - more than enough for
a handful of keywords across 2 countries run once a day.
"""
import os
import requests

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"


def fetch_jobs(keyword: str, country: str, results: int = 20) -> list[dict]:
    """Fetch jobs for a single keyword/country pair. Returns normalized job dicts."""
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError(
            "Missing ADZUNA_APP_ID / ADZUNA_APP_KEY environment variables. "
            "Get free credentials at https://developer.adzuna.com/"
        )

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results,
        "what": keyword,
        "content-type": "application/json",
    }

    resp = requests.get(BASE_URL.format(country=country), params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("results", []):
        jobs.append({
            "id": f"adzuna-{item.get('id')}",
            "source": "adzuna",
            "title": item.get("title", "").strip(),
            "company": (item.get("company") or {}).get("display_name", "Unknown"),
            "location": (item.get("location") or {}).get("display_name", ""),
            "url": item.get("redirect_url", ""),
            "description": (item.get("description") or "")[:1500],
            "posted_at": item.get("created", ""),
            "search_keyword": keyword,
            "country": country,
        })
    return jobs

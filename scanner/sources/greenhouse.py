"""
Greenhouse public job board adapter.

Any company using Greenhouse (like MOIA) exposes a free, unauthenticated
JSON API listing every open role - no scraping, no login, no ToS issue:
  https://boards-api.greenhouse.io/v1/boards/<company-slug>/jobs

Find a company's slug from its careers URL, e.g.:
  job-boards.eu.greenhouse.io/moia/jobs/...  ->  slug is "moia"
"""
import requests

BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"


def fetch_jobs(company_slug: str) -> list[dict]:
    resp = requests.get(BASE_URL.format(slug=company_slug), timeout=20)
    if resp.status_code == 404:
        # Slug doesn't exist / company doesn't use Greenhouse's public board API
        return []
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("jobs", []):
        jobs.append({
            "id": f"greenhouse-{item.get('id')}",
            "source": "greenhouse",
            "title": item.get("title", "").strip(),
            "company": company_slug,
            "location": (item.get("location") or {}).get("name", ""),
            "url": item.get("absolute_url", ""),
            "description": "",  # full description requires a second call; kept light for now
            "posted_at": item.get("updated_at", ""),
            "search_keyword": None,
            "country": None,
        })
    return jobs

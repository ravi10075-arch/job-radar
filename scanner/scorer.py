"""
Rule-based job scorer. No API key, no cost, no billing setup needed.

Scores each posting 0-100 by matching weighted keywords against the job's
title and description. Title matches count more than description matches
(a title mention means the role IS that thing; a description mention just
means it's referenced somewhere in the requirements).

This is intentionally transparent and tunable: every score comes from
keywords you can see and edit yourself in config.yaml, unlike an LLM's
opaque judgment. It won't catch nuance an LLM would (e.g. a job that
clearly wants your skillset but never uses your exact terms), so treat
low scores as "check manually if the title looks interesting" rather than
a guaranteed miss.
"""
import re


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).lower()


def score_job(job: dict, keyword_weights: dict) -> dict:
    title = _normalize(job.get("title", ""))
    description = _normalize(job.get("description", ""))

    raw_score = 0
    matched = []

    for keyword, weight in keyword_weights.items():
        kw = keyword.lower()
        in_title = kw in title
        in_desc = kw in description

        if in_title:
            raw_score += weight  # full weight for a title hit
            matched.append(f"{keyword} (title)")
        elif in_desc:
            raw_score += weight * 0.4  # partial credit for a description-only hit
            matched.append(keyword)

    # Scale raw_score into a 0-100 range. A single strong title match (weight
    # ~9-10) should already read as a solid match on its own, with additional
    # matches pushing it toward 100 - not require hitting every keyword in
    # the whole list (that would crush all real-world scores near zero).
    SCALE = 6
    normalized = min(100, round(raw_score * SCALE))

    if matched:
        reason = "Matched: " + ", ".join(matched[:4])
        if len(matched) > 4:
            reason += f" (+{len(matched) - 4} more)"
    else:
        reason = "No keyword overlap with your profile terms"

    job["match_score"] = normalized
    job["match_reason"] = reason
    return job


def score_all(jobs: list[dict], keyword_weights: dict) -> list[dict]:
    return [score_job(job, keyword_weights) for job in jobs]

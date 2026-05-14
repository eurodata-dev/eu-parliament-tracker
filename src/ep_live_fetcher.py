"""
ep_live_fetcher.py — HowTheyVote API fetcher for recent EP roll-call votes.

Note: The originally specified DOCEO XML endpoint
  (https://www.europarl.europa.eu/doceo/document/PV-10-{date}-RCV_EN.xml)
is protected by AWS WAF / CloudFront (returns HTTP 202 + empty body for all
non-browser clients — confirmed by x-amzn-waf-action: challenge header).
This fetcher uses the HowTheyVote.eu open API instead, which provides the
same EP roll-call vote data in structured JSON and is publicly accessible.

API: https://howtheyvote.eu/api/votes
  - List endpoint: GET /votes?page=N&per_page=50  (most recent first)
  - Detail endpoint: GET /votes/{id}              (includes stats.by_group)

Logic:
  STEP 1  Fetch pages of recent votes until we have enough candidates or
          hit the 60-day lookback limit.
  STEP 2  For each candidate vote, fetch the detail endpoint to get
          per-group vote counts (FOR / AGAINST / ABSTENTION).
          Stop after MAX_DETAIL_CALLS to keep runtime short.
          Apply 1-second delay between requests.
  STEP 3  Emit one row per (vote, political_group) using the dominant
          position for that group.
  STEP 4  Save to data/recent/ep_live_{today}.csv; return the DataFrame.

Output schema: member_name, political_group, policy_topic, vote, date
"""

from __future__ import annotations

import logging
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

from config import settings

logger = logging.getLogger(__name__)

_OUTPUT_DIR      = Path(settings.DATA_DIR) / "recent"
_API_LIST        = "https://howtheyvote.eu/api/votes"
_API_DETAIL      = "https://howtheyvote.eu/api/votes/{vote_id}"
_TIMEOUT         = 20
_REQUEST_DELAY   = 1       # seconds between requests
_LOOKBACK_DAYS   = 60
_MAX_SESSIONS    = 5       # stop after this many unique session dates
_MAX_DETAIL_CALLS = 60     # cap total detail API calls (≈60 sec max)
_PAGE_SIZE       = 50

SCHEMA_COLUMNS = ["member_name", "political_group", "policy_topic", "vote", "date"]

# HowTheyVote group codes → canonical short labels used in the project
_GROUP_MAP: dict[str, str] = {
    "EPP":       "EPP",
    "SD":        "S&D",
    "PFE":       "Patriots for Europe",
    "ECR":       "ECR",
    "RENEW":     "Renew",
    "GREEN_EFA": "Greens/EFA",
    "GUE_NGL":   "The Left",
    "NI":        "NI",
    "ESN":       "ESN",
}

# HowTheyVote position values → canonical vote label
_POSITION_MAP: dict[str, str] = {
    "FOR":        "FOR",
    "AGAINST":    "AGAINST",
    "ABSTENTION": "ABSTAIN",
}


def _safe_get(url: str, params: dict | None = None) -> dict | None:
    """GET url, return parsed JSON or None on any error."""
    try:
        resp = requests.get(url, params=params, timeout=_TIMEOUT)
        if resp.status_code == 404:
            return None
        if resp.status_code == 200:
            return resp.json()
        logger.warning("Unexpected status %s for %s", resp.status_code, url)
        return None
    except requests.exceptions.RequestException as exc:
        logger.warning("Request failed for %s: %s", url, exc)
        return None


def _rows_from_detail(vote_detail: dict) -> list[dict]:
    """Convert a HowTheyVote vote detail record into per-group rows."""
    rows: list[dict] = []

    ts   = vote_detail.get("timestamp", "")[:10]   # YYYY-MM-DD
    title = (
        (vote_detail.get("procedure") or {}).get("title")
        or vote_detail.get("display_title")
        or "Unknown"
    )
    topic = title[:100]

    by_group = (vote_detail.get("stats") or {}).get("by_group", [])
    for entry in by_group:
        grp_code = (entry.get("group") or {}).get("code", "")
        grp_label = _GROUP_MAP.get(grp_code, grp_code)
        if not grp_label:
            continue

        stats = entry.get("stats", {})
        counts = {
            "FOR":     int(stats.get("FOR", 0)),
            "AGAINST": int(stats.get("AGAINST", 0)),
            "ABSTAIN": int(stats.get("ABSTENTION", 0)),
        }

        if not any(counts.values()):
            continue

        dominant = max(counts, key=counts.__getitem__)

        rows.append({
            "member_name":     f"{grp_label} (group)",
            "political_group": grp_label,
            "policy_topic":    topic,
            "vote":            dominant,
            "date":            ts,
        })

    return rows


def run() -> pd.DataFrame:
    """Fetch recent EP RCV data via HowTheyVote API, save to CSV, return DataFrame.

    Fetches votes from the last 60 days, limited to MAX_SESSIONS unique session
    dates and MAX_DETAIL_CALLS detail API requests.  Deletes old ep_live_*.csv
    files before writing a fresh one.  Never raises — always returns a DataFrame
    with the 5-column schema.
    """
    today     = date.today()
    today_str = today.strftime("%Y-%m-%d")
    cutoff    = (today - timedelta(days=_LOOKBACK_DAYS)).isoformat()

    print(f"\nHowTheyVote fetcher — recent EP votes since {cutoff}")

    # ── STEP 1: collect candidate vote IDs from list pages ────────────────────

    candidates: list[dict] = []   # [{id, timestamp, display_title}]

    page = 1
    while True:
        print(f"  Fetching list page {page}…")
        body = _safe_get(_API_LIST, params={"page": page, "per_page": _PAGE_SIZE})
        time.sleep(_REQUEST_DELAY)

        if not body or "results" not in body:
            break

        for item in body["results"]:
            ts = item.get("timestamp", "")[:10]
            if ts < cutoff:
                # API is sorted newest-first; once we pass the cutoff we're done
                break
            candidates.append({
                "id":            item["id"],
                "timestamp":     ts,
                "display_title": item.get("display_title", ""),
            })
        else:
            # The inner loop completed without hitting cutoff — check next page
            if not body.get("has_next"):
                break
            page += 1
            continue

        # Broke out of inner loop because we hit cutoff date
        break

    print(f"  Candidates within {_LOOKBACK_DAYS} days: {len(candidates)}")

    if not candidates:
        print("WARNING: no recent EP votes found.")
        return pd.DataFrame(columns=SCHEMA_COLUMNS)

    # ── STEP 2: fetch detail for each candidate (capped at MAX_DETAIL_CALLS) ──

    all_rows:       list[dict] = []
    session_dates:  set[str]   = set()
    detail_calls    = 0

    for cand in candidates:
        if detail_calls >= _MAX_DETAIL_CALLS:
            break
        if len(session_dates) >= _MAX_SESSIONS and cand["timestamp"] not in session_dates:
            break

        vote_id = cand["id"]
        detail  = _safe_get(_API_DETAIL.format(vote_id=vote_id))
        detail_calls += 1
        time.sleep(_REQUEST_DELAY)

        if not detail:
            continue

        rows = _rows_from_detail(detail)
        if rows:
            all_rows.extend(rows)
            session_dates.add(cand["timestamp"])
            print(
                f"  {cand['timestamp']}  {len(rows):2d} group-rows  "
                f"'{cand['display_title'][:55]}'"
            )

    print(
        f"\n  Detail calls: {detail_calls}  "
        f"Sessions: {len(session_dates)}  "
        f"Total rows: {len(all_rows)}"
    )

    if not all_rows:
        print("WARNING: no parseable vote data found.")
        return pd.DataFrame(columns=SCHEMA_COLUMNS)

    # ── STEP 3: build DataFrame ───────────────────────────────────────────────

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df[SCHEMA_COLUMNS].reset_index(drop=True)

    # ── STEP 4: save CSV ──────────────────────────────────────────────────────

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for old in _OUTPUT_DIR.glob("ep_live_*.csv"):
        old.unlink()

    out_path = _OUTPUT_DIR / f"ep_live_{today_str}.csv"
    df.to_csv(out_path, index=False)

    dates_label = ", ".join(sorted(session_dates, reverse=True))
    print(
        f"\nLive data: {len(df)} rows from {len(session_dates)} session(s)"
        f" (dates: {dates_label})"
    )
    print(f"Saved -> {out_path}")

    return df


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )
    run()

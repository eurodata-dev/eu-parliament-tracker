"""
test_full_pipeline.py — End-to-end EU Policy Intelligence pipeline validation.

Run from the project root:
    python test_full_pipeline.py
"""

import sys
from pathlib import Path

# Allow imports from src/ when running from the project root.
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd

from eu_api import fetch_all_votes, fetch_eu_votes, search_policy_topic
from analysis_agent import analyze_policy, generate_ai_insight
import ep_live_fetcher
from config import settings

_SEP = "═" * 54


def section(title: str) -> None:
    print(f"\n{_SEP}")
    print(f"  {title}")
    print(_SEP)


# ── 1. DATA TEST ──────────────────────────────────────────────────────────────
section("DATA TEST")
_all_votes = None
try:
    _all_votes = fetch_all_votes()
    print(f"Rows loaded : {len(_all_votes)}")
    print(f"Columns     : {list(_all_votes.columns)}")
    print(f"\nSample (first 3 rows):")
    print(_all_votes.head(3).to_string(index=False))
except Exception as exc:
    print(f"[ERROR] {exc}")


# ── 2. TOPIC FILTER TEST ──────────────────────────────────────────────────────
section("TOPIC FILTER TEST")
try:
    filtered = fetch_eu_votes("AI")
    if filtered.empty:
        print("No rows matched query 'AI'.")
    else:
        print(f"Rows matched for query 'AI': {len(filtered)}")
        print(filtered.to_string(index=False))
except Exception as exc:
    print(f"[ERROR] {exc}")


# ── 3. SUMMARY TEST ───────────────────────────────────────────────────────────
section("SUMMARY TEST")
_summary = None
_topic = None
try:
    votes_df = _all_votes if _all_votes is not None else fetch_all_votes()
    _topic = search_policy_topic("AI") or "AI Act"
    _summary = analyze_policy(votes_df, _topic)
    print(f"Topic resolved: '{_topic}'")
    print(f"Groups in summary: {len(_summary)}\n")
    for group, counts in sorted(_summary.items()):
        print(
            f"  {group:<14}  FOR: {counts['FOR']:<3}  "
            f"AGAINST: {counts['AGAINST']:<3}  ABSTAIN: {counts['ABSTAIN']}"
        )
except ValueError as exc:
    print(f"[WARN] Topic not found — {exc}")
except Exception as exc:
    print(f"[ERROR] {exc}")


# ── 4. AI INSIGHT TEST ────────────────────────────────────────────────────────
section("AI INSIGHT TEST")
try:
    if _summary is None or _topic is None:
        votes_df = _all_votes if _all_votes is not None else fetch_all_votes()
        _topic = search_policy_topic("AI") or "AI Act"
        _summary = analyze_policy(votes_df, _topic)

    print(f"Sending summary for '{_topic}' to Mistral (may take ~30–180s)...\n")
    insight = generate_ai_insight(_summary, _topic)
    print(insight)
except ValueError as exc:
    print(f"[WARN] Topic not found — skipping AI insight: {exc}")
except Exception as exc:
    print(f"[ERROR] {exc}")


# ── 5. LIVE DATA LAYER TEST ───────────────────────────────────────────────────
section("LIVE DATA LAYER TEST")
_REQUIRED_COLUMNS = {"member_name", "political_group", "policy_topic", "vote", "date"}
_RECENT_DIR = Path(settings.DATA_DIR) / "recent"

try:
    print("Calling ep_live_fetcher.run() (last 30 days)…")
    out_path = ep_live_fetcher.run()
    print(f"Fetcher wrote: {out_path}")
except RuntimeError as exc:
    print(f"[WARN] EP API unreachable — live data test skipped: {exc}")
    out_path = None
except Exception as exc:
    print(f"[WARN] Unexpected error from live fetcher — skipping: {exc}")
    out_path = None

if out_path is not None:
    csv_files = sorted(_RECENT_DIR.glob("*.csv")) if _RECENT_DIR.exists() else []
    if not csv_files:
        print("[WARN] data/recent/ exists but contains no CSV files.")
    else:
        print(f"CSV files in data/recent/: {len(csv_files)}")
        for f in csv_files:
            print(f"  {f.name}")

        recent_df = pd.read_csv(csv_files[-1])
        missing = _REQUIRED_COLUMNS - set(recent_df.columns)
        if missing:
            print(f"[ERROR] Missing required columns: {missing}")
        else:
            print(f"\nSchema OK — all 5 required columns present.")
            print(f"Row count : {len(recent_df)}")
            print(f"\nFirst 3 rows:")
            print(recent_df.head(3).to_string(index=False))


print(f"\n{_SEP}")
print("  PIPELINE TEST COMPLETE")
print(f"{_SEP}\n")

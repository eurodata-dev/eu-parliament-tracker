# EU Policy Intelligence Agent — Complete Project Handoff

This document gives you a full understanding of every file, design decision, data structure, and module in this project. Read it top to bottom before touching anything. No external files are needed — everything is here.

---

## 1. Project Overview

**What it does:**  
An AI-powered system that loads European Parliament voting data, analyzes it, and generates political insights. It has a Streamlit web dashboard as its primary interface and a legacy CLI as a secondary one.

**Current state:**  
Fully working dashboard with mock/sample data. Real HowTheyVote data can be ingested via a script. A "recent change detection" pipeline compares the last 30 days of votes against the historical baseline and generates a plain-English summary.

**Primary goal:**  
Portfolio/demo project showing EU political analytics. Designed to be upgraded progressively: CSV mock data → real EP API data → Claude-powered insights instead of Ollama/mistral.

---

## 2. Project Structure

```
EU Policy Intelligence Agent project/
│
├── src/                          ← All Python source modules
│   ├── app.py                    ← Streamlit dashboard (MAIN UI — run this)
│   ├── config.py                 ← Settings dataclass (reads env vars)
│   ├── eu_api.py                 ← Public API boundary layer for vote data
│   ├── eu_dataset_loader.py      ← Historical data loader (CSV priority chain)
│   ├── data_loader.py            ← Legacy loader (CSV + hardcoded mock fallback)
│   ├── recent_data_loader.py     ← Loads votes from last N days
│   ├── political_comparison_engine.py  ← Computes historical vs recent drift
│   ├── political_ai_explainer.py       ← Converts drift dict → plain English
│   ├── analysis_agent.py         ← Vote aggregation + Ollama AI insight
│   ├── prompts.py                ← LangChain prompt templates (legacy, unused)
│   ├── main.py                   ← Legacy CLI interface
│   └── download_sample_data.py   ← Script that generated the sample CSV
│
├── data/
│   ├── raw/
│   │   ├── eu_votes_sample.csv        ← 32-row sample dataset (primary for demo)
│   │   └── real_votes/                ← HowTheyVote raw CSVs (optional)
│   │       ├── member_votes.csv       ← Large file: vote_id, member_id, position
│   │       ├── votes.csv              ← vote metadata (title, timestamp)
│   │       ├── members.csv            ← MEP names
│   │       ├── groups.csv             ← Political group codes and labels
│   │       └── group_memberships.csv  ← MEP → group → term mapping
│   └── processed/
│       └── eu_votes_real.csv          ← Output of load_real_votes.py (if run)
│
├── scripts/
│   └── load_real_votes.py        ← Ingestion pipeline for HowTheyVote data
│
├── test_full_pipeline.py         ← End-to-end test (no pytest, just run it)
├── test_eu_api.py                ← Quick API endpoint sanity check
├── requirements.txt
├── README.md
└── PROJECT_CONTEXT.md            ← Project notes (keep updated)
```

---

## 3. How to Run

### Prerequisites

```bash
# Python 3.11+
pip install -r requirements.txt

# requirements.txt contents:
# langchain>=0.3.0
# langchain-anthropic>=0.3.0
# langchain-core>=0.3.0
# requests>=2.31.0
# pandas>=2.1.0
# streamlit>=1.35.0
# python-dotenv>=1.0.0
```

### Environment variables

Create a `.env` file at the project root:
```
ANTHROPIC_API_KEY=your_key_here
ENV=development
DEMO_MODE=false
```

`DEMO_MODE=true` caps the historical dataset at 5,000 rows and disables Ollama AI calls — use this for demos without a running Ollama server.

### Run the dashboard

```bash
cd src
streamlit run app.py
```

### Run the legacy CLI

```bash
cd src
python main.py
```

### Run the end-to-end test

```bash
python test_full_pipeline.py
```

### Ingest real HowTheyVote data (optional)

```bash
# Drop these files into data/raw/real_votes/:
#   member_votes.csv, votes.csv, members.csv, groups.csv, group_memberships.csv
python scripts/load_real_votes.py
# Output: data/processed/eu_votes_real.csv
# App will automatically use it on next start (highest priority source)
```

### Activate AI insights (optional)

```bash
ollama serve
ollama pull mistral
# The dashboard's "AI Insight" button will now work
```

---

## 4. Universal Data Schema

Every module in this project guarantees the same 5-column schema. This is the contract that lets layers be swapped independently.

| Column | Type | Values |
|---|---|---|
| `member_name` | str | Full MEP name (e.g. "Manfred Weber") |
| `political_group` | str | Group abbreviation: EPP, S&D, Renew, Greens/EFA, ECR, ID |
| `policy_topic` | str | Topic label: "AI Act", "Climate Policy", "Migration Policy", "Digital Services Act", "Green Deal", "Cybersecurity" |
| `vote` | str | FOR, AGAINST, ABSTAIN |
| `date` | pd.Timestamp | Plenary vote date |

**Important:** The real HowTheyVote dataset uses full group names ("Progressive Alliance of Socialists and Democrats" instead of "S&D") and has topic names like "Mardi - demande du groupe GUE/NGL" — these are raw procedural titles, not cleaned labels like in the sample CSV. This is a known gap.

---

## 5. Data Source Priority Chain

```
eu_dataset_loader.get_eu_votes()
    ├── data/processed/eu_votes_real.csv    ← Priority 1 (produced by load_real_votes.py)
    ├── data/raw/eu_votes_sample.csv        ← Priority 2 (32-row sample, bundled)
    └── hardcoded 12-record fallback        ← Priority 3 (offline / CI)

recent_data_loader.load_recent_votes(days=30)
    ├── data/recent/*.csv                   ← Priority 1
    ├── data/processed/*.csv                ← Priority 2
    └── empty DataFrame (correct schema)    ← Graceful fallback
```

---

## 6. Module Reference — Full Source Code + Explanation

### 6.1 `src/config.py`

**Purpose:** Single place to read environment variables. Every module that needs settings imports `settings` from here.

```python
import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    DATA_DIR: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "..", "data"))


settings = Settings()
```

`DATA_DIR` resolves to the `data/` folder relative to `src/`, regardless of the working directory when the script is launched. Every file path in the project is built from `settings.DATA_DIR`.

---

### 6.2 `src/eu_dataset_loader.py`

**Purpose:** Load historical EU Parliament voting records from whichever data source is currently active. This is the authoritative historical data source. Callers never need to know which source is active.

**Public function:** `get_eu_votes() -> pd.DataFrame`

**Source priority:** real CSV → sample CSV → hardcoded fallback

```python
"""
eu_dataset_loader.py — EU Parliament voting data ingestion layer.

Source priority (highest → lowest):
  1. data/processed/eu_votes_real.csv   — produced by scripts/load_real_votes.py
  2. data/raw/eu_votes_sample.csv       — small sample dataset
  3. hardcoded 12-record fallback       — offline / development
"""

from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd
from config import settings

logger = logging.getLogger(__name__)

SCHEMA: list[str] = [
    "member_name",
    "political_group",
    "policy_topic",
    "vote",
    "date",
]

_FALLBACK_RECORDS: list[dict] = [
    # AI Act — March 2024
    {"member_name": "Dragos Tudorache",     "political_group": "Renew",      "policy_topic": "AI Act",               "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Brando Benifei",       "political_group": "S&D",        "policy_topic": "AI Act",               "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Peter Kofod",          "political_group": "ID",         "policy_topic": "AI Act",               "vote": "AGAINST", "date": "2024-03-13"},
    # Climate Policy — June 2023
    {"member_name": "Mohammed Chahim",      "political_group": "S&D",        "policy_topic": "Climate Policy",       "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Bas Eickhout",         "political_group": "Greens/EFA", "policy_topic": "Climate Policy",       "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Alexandr Vondra",      "political_group": "ECR",        "policy_topic": "Climate Policy",       "vote": "AGAINST", "date": "2023-06-22"},
    # Digital Services Act — July 2022
    {"member_name": "Christel Schaldemose", "political_group": "S&D",        "policy_topic": "Digital Services Act", "vote": "FOR",     "date": "2022-07-05"},
    {"member_name": "Andreas Schwab",       "political_group": "EPP",        "policy_topic": "Digital Services Act", "vote": "FOR",     "date": "2022-07-05"},
    {"member_name": "Marcel de Graaff",     "political_group": "ID",         "policy_topic": "Digital Services Act", "vote": "AGAINST", "date": "2022-07-05"},
    # Migration Policy — April 2024
    {"member_name": "Roberta Metsola",      "political_group": "EPP",        "policy_topic": "Migration Policy",     "vote": "FOR",     "date": "2024-04-10"},
    {"member_name": "Tineke Strik",         "political_group": "Greens/EFA", "policy_topic": "Migration Policy",     "vote": "AGAINST", "date": "2024-04-10"},
    {"member_name": "Fabrice Leggeri",      "political_group": "ID",         "policy_topic": "Migration Policy",     "vote": "ABSTAIN", "date": "2024-04-10"},
]


def _load_from_real_votes() -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df[SCHEMA]


def _load_from_csv() -> pd.DataFrame:
    csv_path = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    return df[SCHEMA]


def _load_fallback() -> pd.DataFrame:
    df = pd.DataFrame(_FALLBACK_RECORDS)
    df["date"] = pd.to_datetime(df["date"])
    return df[SCHEMA]


def get_eu_votes() -> pd.DataFrame:
    """Return a DataFrame of EU Parliament voting records.

    Guaranteed schema regardless of active source:
        member_name, political_group, policy_topic, vote, date
    """
    real_path   = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    sample_path = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"

    if real_path.exists():
        return _load_from_real_votes()
    if sample_path.exists():
        return _load_from_csv()
    return _load_fallback()
```

---

### 6.3 `src/eu_api.py`

**Purpose:** The public API boundary layer. App code calls this — never `eu_dataset_loader` directly. If the data source ever changes, only this file and `eu_dataset_loader` change; `app.py` and `analysis_agent.py` are unaffected.

**Public functions:**
- `fetch_all_votes() -> pd.DataFrame` — returns the full dataset unfiltered
- `fetch_eu_votes(query: str) -> pd.DataFrame` — resolves query → topic → filtered rows
- `search_policy_topic(query: str) -> str | None` — 3-pass topic matching

```python
"""
eu_api.py — EU Parliament data access layer.

Data flow:
    caller → eu_api.py → eu_dataset_loader.get_eu_votes() → CSV / EP Open Data
"""

from __future__ import annotations
import logging
import pandas as pd
from eu_dataset_loader import SCHEMA, get_eu_votes

logger = logging.getLogger(__name__)
_EXPECTED_COLUMNS: list[str] = SCHEMA


def _normalize(text: str) -> str:
    return text.strip().lower()


def _available_topics(votes_df: pd.DataFrame) -> list[str]:
    return sorted(votes_df["policy_topic"].unique().tolist())


def search_policy_topic(query: str) -> str | None:
    """Resolve a free-text query to the closest known policy topic.

    Three-pass matching (most to least strict):
        1. Exact match (case-insensitive)
        2. Substring — topic contains query, or query contains topic
        3. Word-overlap — any query word appears in a topic name

    Returns the exact policy_topic label, or None if nothing matches.
    """
    if not query or not query.strip():
        return None

    votes_df = get_eu_votes()
    topics = _available_topics(votes_df)
    q = _normalize(query)

    # Pass 1 — exact
    for topic in topics:
        if _normalize(topic) == q:
            return topic

    # Pass 2 — substring
    substring_matches = [t for t in topics if q in _normalize(t) or _normalize(t) in q]
    if len(substring_matches) == 1:
        return substring_matches[0]
    if len(substring_matches) > 1:
        return min(substring_matches, key=len)  # shortest = most specific

    # Pass 3 — word-overlap
    query_words = set(q.split())
    word_matches = [t for t in topics if query_words & set(_normalize(t).split())]
    if word_matches:
        return min(word_matches, key=len)

    return None


def fetch_all_votes() -> pd.DataFrame:
    """Return the full voting dataset — no topic filter. Used by app.py for KPIs."""
    return get_eu_votes()


def fetch_eu_votes(query: str) -> pd.DataFrame:
    """Return voting records matching a free-text policy topic query."""
    topic = search_policy_topic(query)
    if topic is None:
        return pd.DataFrame(columns=_EXPECTED_COLUMNS)
    votes_df = get_eu_votes()
    return votes_df[votes_df["policy_topic"] == topic].reset_index(drop=True)
```

---

### 6.4 `src/data_loader.py`

**Purpose:** Legacy loader. Still used by `main.py` (the CLI). Do not remove — it provides `get_mock_votes()` as the emergency fallback that `load_votes()` calls. The newer `eu_dataset_loader.py` supersedes this for the Streamlit app.

```python
import requests
import pandas as pd
from pathlib import Path
from config import settings


def load_csv(filename: str) -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / filename
    return pd.read_csv(path)


def fetch_url(url: str, params: dict | None = None) -> dict:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_mock_votes() -> pd.DataFrame:
    """12-record hardcoded fallback — emergency use only."""
    records = [
        {"member_name": "Dragos Tudorache",    "political_group": "Renew",      "policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
        {"member_name": "Brando Benifei",      "political_group": "S&D",        "policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
        {"member_name": "Peter Kofod",         "political_group": "ID",         "policy_topic": "AI Act",             "vote": "AGAINST", "date": "2024-03-13"},
        {"member_name": "Mohammed Chahim",     "political_group": "S&D",        "policy_topic": "Climate Policy",     "vote": "FOR",     "date": "2023-06-22"},
        {"member_name": "Bas Eickhout",        "political_group": "Greens/EFA", "policy_topic": "Climate Policy",     "vote": "FOR",     "date": "2023-06-22"},
        {"member_name": "Alexandr Vondra",     "political_group": "ECR",        "policy_topic": "Climate Policy",     "vote": "AGAINST", "date": "2023-06-22"},
        {"member_name": "Christel Schaldemose","political_group": "S&D",        "policy_topic": "Digital Services Act","vote": "FOR",    "date": "2022-07-05"},
        {"member_name": "Andreas Schwab",      "political_group": "EPP",        "policy_topic": "Digital Services Act","vote": "FOR",    "date": "2022-07-05"},
        {"member_name": "Marcel de Graaff",    "political_group": "ID",         "policy_topic": "Digital Services Act","vote": "AGAINST","date": "2022-07-05"},
        {"member_name": "Roberta Metsola",     "political_group": "EPP",        "policy_topic": "Migration Policy",   "vote": "FOR",     "date": "2024-04-10"},
        {"member_name": "Tineke Strik",        "political_group": "Greens/EFA", "policy_topic": "Migration Policy",   "vote": "AGAINST", "date": "2024-04-10"},
        {"member_name": "Fabrice Leggeri",     "political_group": "ID",         "policy_topic": "Migration Policy",   "vote": "ABSTAIN", "date": "2024-04-10"},
    ]
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_votes() -> pd.DataFrame:
    """Primary source: data/raw/eu_votes_sample.csv. Fallback: get_mock_votes()."""
    csv_path = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df["date"] = pd.to_datetime(df["date"])
        return df
    return get_mock_votes()
```

---

### 6.5 `src/recent_data_loader.py`

**Purpose:** Pure data layer for "recent" votes. Reads from `data/recent/` (preferred) or `data/processed/` (fallback), filters to the last N days, and returns the standard 5-column schema. No AI, no merging with historical data.

**Public function:** `load_recent_votes(days: int = 30) -> pd.DataFrame`

**Private helper:** `_load_recent_csv_files()` — globs all `.csv` files in the chosen directory and concatenates them.

```python
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from config import settings

SCHEMA_COLUMNS = ["member_name", "political_group", "policy_topic", "vote", "date"]

_RECENT_DIR    = Path(settings.DATA_DIR) / "recent"
_PROCESSED_DIR = Path(settings.DATA_DIR) / "processed"


def _load_recent_csv_files() -> pd.DataFrame:
    """Load and concatenate all CSV files from data/recent/ or data/processed/."""
    source_dir = _RECENT_DIR if _RECENT_DIR.exists() else _PROCESSED_DIR

    if not source_dir.exists():
        return pd.DataFrame(columns=SCHEMA_COLUMNS)

    csv_files = sorted(source_dir.glob("*.csv"))
    if not csv_files:
        return pd.DataFrame(columns=SCHEMA_COLUMNS)

    frames = []
    for csv_path in csv_files:
        try:
            df = pd.read_csv(csv_path)
            frames.append(df)
        except Exception:
            continue

    if not frames:
        return pd.DataFrame(columns=SCHEMA_COLUMNS)

    return pd.concat(frames, ignore_index=True)


def load_recent_votes(days: int = 30) -> pd.DataFrame:
    """Load EP vote records from the last N days.

    Returns an empty DataFrame with the correct schema if no data is found
    or no rows fall within the requested window.
    """
    df = _load_recent_csv_files()

    if df.empty:
        return df

    # Keep only schema columns that are present; fill missing ones with pd.NA
    present = [col for col in SCHEMA_COLUMNS if col in df.columns]
    df = df[present].copy()
    for col in SCHEMA_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    # Parse dates — coerce unparseable values to NaT
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    if df.empty:
        return df[SCHEMA_COLUMNS]

    # Normalise timezone-aware dates to UTC-naive for comparison
    if df["date"].dt.tz is not None:
        df["date"] = df["date"].dt.tz_convert("UTC").dt.tz_localize(None)

    cutoff = datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    df = df[df["date"] >= cutoff].copy()

    return df[SCHEMA_COLUMNS].reset_index(drop=True)
```

**Key design decisions:**
- Graceful at every failure point — missing directory, unreadable file, malformed date: all produce an empty DataFrame, never a crash.
- Timezone normalization: tz-aware dates are converted to UTC-naive before the cutoff comparison, so mixed-timezone files don't crash.
- Does NOT merge with historical data — that is `political_comparison_engine`'s job.

---

### 6.6 `src/political_comparison_engine.py`

**Purpose:** Pure analytics. Takes two DataFrames (historical, recent) and returns a structured dict showing how voting behavior changed. No LLM, no visualization, no I/O.

**Public functions:**
- `compute_group_behavior(df) -> pd.DataFrame` — per-group vote shares (% FOR / AGAINST / ABSTAIN)
- `compute_topic_behavior(df) -> pd.DataFrame` — same, grouped by policy_topic
- `compare_behavior(historical_df, recent_df) -> dict` — returns the full drift analysis

**Output structure of `compare_behavior`:**
```python
{
    "group_drift": {
        "EPP":        {"delta_FOR": +5.2, "delta_AGAINST": -3.1, "delta_ABSTAIN": -2.1},
        "S&D":        {"delta_FOR": -1.0, "delta_AGAINST": +0.5, "delta_ABSTAIN": +0.5},
        # ... one entry per group that appears in either dataset
    },
    "topic_drift": {
        "AI Act":     {"delta_FOR": +10.0, "delta_AGAINST": -5.0, "delta_ABSTAIN": -5.0},
        # ... one entry per topic that appears in either dataset
    },
    "summary": {
        "most_changed_group":          "EPP",
        "most_changed_topic":          "AI Act",
        "overall_polarization_change": +2.3,    # pp; positive = more polarized
        "top_5_changed_groups":        ["EPP", "Greens/EFA", "ID", "ECR", "S&D"],
        "top_5_changed_topics":        ["AI Act", "Climate Policy", ...],
    }
}
```

**Polarization definition:** Mean absolute deviation of `pct_FOR` from 50 across all groups. A value near 0 means consensus, higher means divergence. `overall_polarization_change` = recent − historical; positive = more polarized recently.

**Top changers scoring:** Sum of `abs(delta_FOR) + abs(delta_AGAINST) + abs(delta_ABSTAIN)` — so a group that shifted +20 FOR and −20 AGAINST ranks higher than one that shifted +5 across the board.

```python
import pandas as pd

VOTE_LABELS = ["FOR", "AGAINST", "ABSTAIN"]


def _vote_shares(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if df.empty or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, "pct_FOR", "pct_AGAINST", "pct_ABSTAIN"])

    counts = (
        df.groupby([group_col, "vote"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=VOTE_LABELS, fill_value=0)
    )
    totals = counts.sum(axis=1).replace(0, pd.NA)
    shares = (counts.div(totals, axis=0) * 100).round(2)
    shares.columns = [f"pct_{v}" for v in VOTE_LABELS]
    return shares.reset_index()


def compute_group_behavior(df: pd.DataFrame) -> pd.DataFrame:
    return _vote_shares(df, "political_group")


def compute_topic_behavior(df: pd.DataFrame) -> pd.DataFrame:
    return _vote_shares(df, "policy_topic")


def _drift_table(hist: pd.DataFrame, recent: pd.DataFrame, key_col: str) -> dict:
    hist_indexed   = hist.set_index(key_col)   if not hist.empty   else pd.DataFrame()
    recent_indexed = recent.set_index(key_col) if not recent.empty else pd.DataFrame()

    all_keys  = set(hist_indexed.index) | set(recent_indexed.index)
    share_cols = ["pct_FOR", "pct_AGAINST", "pct_ABSTAIN"]
    result = {}
    for key in sorted(all_keys):
        hist_row   = hist_indexed.loc[key, share_cols]   if key in hist_indexed.index   else pd.Series([0.0]*3, index=share_cols)
        recent_row = recent_indexed.loc[key, share_cols] if key in recent_indexed.index else pd.Series([0.0]*3, index=share_cols)
        delta = (recent_row - hist_row).round(2)
        result[key] = {
            "delta_FOR":     delta["pct_FOR"],
            "delta_AGAINST": delta["pct_AGAINST"],
            "delta_ABSTAIN": delta["pct_ABSTAIN"],
        }
    return result


def _top_changers(drift: dict, n: int = 5) -> list[str]:
    scored = {
        key: abs(v["delta_FOR"]) + abs(v["delta_AGAINST"]) + abs(v["delta_ABSTAIN"])
        for key, v in drift.items()
    }
    return sorted(scored, key=scored.get, reverse=True)[:n]


def _polarization(df: pd.DataFrame) -> float:
    if df.empty or "pct_FOR" not in df.columns:
        return 0.0
    return round(float((df["pct_FOR"] - 50.0).abs().mean()), 2)


def compare_behavior(historical_df: pd.DataFrame, recent_df: pd.DataFrame) -> dict:
    hist_groups   = compute_group_behavior(historical_df)
    recent_groups = compute_group_behavior(recent_df)
    hist_topics   = compute_topic_behavior(historical_df)
    recent_topics = compute_topic_behavior(recent_df)

    group_drift = _drift_table(hist_groups,  recent_groups,  "political_group")
    topic_drift = _drift_table(hist_topics,  recent_topics,  "policy_topic")

    top_groups  = _top_changers(group_drift)
    top_topics  = _top_changers(topic_drift)

    pol_hist   = _polarization(hist_groups)
    pol_recent = _polarization(recent_groups)

    summary = {
        "most_changed_group":          top_groups[0] if top_groups else None,
        "most_changed_topic":          top_topics[0] if top_topics else None,
        "overall_polarization_change": round(pol_recent - pol_hist, 2),
        "top_5_changed_groups":        top_groups,
        "top_5_changed_topics":        top_topics,
    }
    return {"group_drift": group_drift, "topic_drift": topic_drift, "summary": summary}
```

---

### 6.7 `src/political_ai_explainer.py`

**Purpose:** Converts the structured dict from `compare_behavior()` into a human-readable plain-English string. Does NOT compute anything — every number it uses comes directly from the input. No LLM, no randomness.

**Public function:** `explain_political_changes(comparison_results: dict, topic: str = None) -> str`

- `topic` is optional. If provided, the explanation focuses on that topic only (case-insensitive substring match).
- Returns a string of 5–10 sentences.
- Journalist-friendly tone: describes observable data changes only, no political ideology interpretation.

```python
def explain_political_changes(comparison_results: dict, topic: str = None) -> str:
    summary     = comparison_results.get("summary", {})
    group_drift = comparison_results.get("group_drift", {})
    topic_drift = comparison_results.get("topic_drift", {})

    if not summary and not group_drift and not topic_drift:
        return "No comparison data is available to explain."

    sentences = []

    if topic:
        matched = {t: v for t, v in topic_drift.items() if topic.lower() in t.lower()}
        if matched:
            sentences.append(f"The following observations focus on recent voting shifts related to '{topic}'.")
        else:
            return f"No data found for topic '{topic}' in the comparison results."
    else:
        sentences.append("Here is an overview of how voting behavior has shifted between the historical and recent periods.")

    most_changed_group = summary.get("most_changed_group")
    if most_changed_group and most_changed_group in group_drift:
        g = group_drift[most_changed_group]
        direction = _dominant_direction(g)
        sentences.append(
            f"The political group that changed its voting behavior the most is {most_changed_group}, "
            f"which moved notably {direction}."
        )

    top_groups = summary.get("top_5_changed_groups", [])
    if len(top_groups) > 1:
        others = ", ".join(top_groups[1:4])
        sentences.append(f"Other groups showing significant shifts include {others}.")

    if topic and matched:
        for topic_name, drift in matched.items():
            direction = _dominant_direction(drift)
            sentences.append(
                f"On '{topic_name}', recent votes have shifted {direction} "
                f"(FOR: {_fmt(drift['delta_FOR'])}, AGAINST: {_fmt(drift['delta_AGAINST'])}, "
                f"ABSTAIN: {_fmt(drift['delta_ABSTAIN'])})."
            )
    else:
        most_changed_topic = summary.get("most_changed_topic")
        if most_changed_topic and most_changed_topic in topic_drift:
            t = topic_drift[most_changed_topic]
            direction = _dominant_direction(t)
            sentences.append(
                f"The policy topic with the largest voting shift is '{most_changed_topic}', "
                f"where support has moved {direction}."
            )
        top_topics = summary.get("top_5_changed_topics", [])
        if len(top_topics) > 1:
            other_topics = ", ".join(f"'{t}'" for t in top_topics[1:4])
            sentences.append(f"Notable shifts also appear in {other_topics}.")

    pol_change = summary.get("overall_polarization_change")
    if pol_change is not None:
        if abs(pol_change) < 1.0:
            sentences.append("Overall, the level of political polarization has remained relatively stable.")
        elif pol_change > 0:
            sentences.append(
                f"Overall polarization has increased by {pol_change:.1f} percentage points, "
                "suggesting groups are diverging more than before."
            )
        else:
            sentences.append(
                f"Overall polarization has decreased by {abs(pol_change):.1f} percentage points, "
                "suggesting some convergence across groups."
            )

    if not topic:
        sentences.append(
            "These changes reflect observable differences in recorded vote counts "
            "and do not imply conclusions about political intent."
        )

    return " ".join(sentences)


def _dominant_direction(drift: dict) -> str:
    mapping = {
        "FOR":     drift.get("delta_FOR",     0.0),
        "AGAINST": drift.get("delta_AGAINST", 0.0),
        "ABSTAIN": drift.get("delta_ABSTAIN", 0.0),
    }
    label    = max(mapping, key=lambda k: abs(mapping[k]))
    value    = mapping[label]
    qualifier = "more" if value >= 0 else "less"
    return f"{qualifier} toward {label} votes"


def _fmt(value: float) -> str:
    return f"{value:+.1f}%"
```

---

### 6.8 `src/analysis_agent.py`

**Purpose:** Aggregates votes into per-group summaries and generates AI insights via Ollama/mistral. Also contains commented-out Claude integration stub.

**Public functions:**
- `build_summary(votes_df) -> VoteSummary` — aggregates a DataFrame into `{"EPP": {"FOR": 2, "AGAINST": 1, "ABSTAIN": 0}, ...}`
- `analyze_policy(votes_df, topic) -> VoteSummary` — filters by topic, then calls `build_summary`
- `generate_ai_insight(summary_dict, topic) -> str` — builds a structured prompt, calls Ollama, validates output
- `compute_vote_metrics(summary_list) -> dict` — pure Python stats (totals, ratios, rankings)
- `compute_political_signals(metrics) -> dict` — consensus score, polarization score, abstention signal, dominant bloc

**Ollama endpoint:** `http://localhost:11434/api/generate` — model `mistral` — timeout `180s`

**Anti-hallucination:** The prompt sends precomputed values to the LLM and instructs it to act only as a text formatter. Output is validated against a forbidden-word list (`validate_output()`). Words like "alliance", "ideology", "unexpected" trigger an error response.

**Claude integration stub (already in the file, commented out):**
```python
# from langchain_anthropic import ChatAnthropic
# from config import settings
# llm = ChatAnthropic(model="claude-sonnet-4-6", api_key=settings.ANTHROPIC_API_KEY)
# return validate_output(llm.invoke(prompt).content)
```

Full source (analysis_agent.py is long — key sections):

```python
import logging
import statistics
from collections import Counter
import requests
import pandas as pd

VoteSummary = dict[str, dict[str, int]]
_VOTE_LABELS = ["FOR", "AGAINST", "ABSTAIN"]


def build_summary(votes_df: pd.DataFrame) -> VoteSummary:
    pivot = (
        votes_df
        .groupby(["political_group", "vote"])
        .size()
        .unstack(fill_value=0)
    )
    for label in _VOTE_LABELS:
        if label not in pivot.columns:
            pivot[label] = 0
    return {
        group: {label: int(pivot.at[group, label]) for label in _VOTE_LABELS}
        for group in pivot.index
    }


def analyze_policy(votes_df: pd.DataFrame, topic: str) -> VoteSummary:
    filtered = votes_df[votes_df["policy_topic"] == topic]
    if filtered.empty:
        raise ValueError(f"No voting records found for topic '{topic}'.")
    return build_summary(filtered)


def validate_output(text: str) -> str:
    forbidden = ["alliance", "aligned", "coalition", "ideology", "unexpected", "supports same"]
    for word in forbidden:
        if word in text.lower():
            return "Error: invalid AI output (hallucination detected)"
    return text


def compute_vote_metrics(summary_list: list[dict]) -> dict:
    enriched = []
    for row in summary_list:
        total = row["FOR"] + row["AGAINST"] + row["ABSTAIN"]
        enriched.append({
            **row,
            "TOTAL":         total,
            "PARTICIPATION": row["FOR"] + row["AGAINST"],
            "FOR_RATIO":     round(row["FOR"] / total, 4) if total else 0.0,
            "AGAINST_RATIO": round(row["AGAINST"] / total, 4) if total else 0.0,
        })
    ranking_for     = sorted(enriched, key=lambda r: r["FOR"], reverse=True)
    ranking_against = sorted(enriched, key=lambda r: r["AGAINST"], reverse=True)
    max_for = ranking_for[0]
    min_for = ranking_for[-1]
    return {
        "groups":           enriched,
        "ranking_for":      ranking_for,
        "ranking_against":  ranking_against,
        "max_for":          max_for,
        "min_for":          min_for,
        "delta_for":        max_for["FOR"] - min_for["FOR"],
    }


def compute_political_signals(metrics: dict) -> dict:
    groups = metrics["groups"]
    if not groups:
        return {"consensus_score": 0.0, "polarization_score": 0.0, "abstention_signal": 0, "dominant_bloc": "N/A"}

    dominant_per_group = [max(_VOTE_LABELS, key=lambda v: g[v]) for g in groups]
    most_common_count  = Counter(dominant_per_group).most_common(1)[0][1]
    consensus_score    = round(most_common_count / len(groups) * 100, 1)
    polarization_score = round(statistics.pstdev([g["FOR"] for g in groups]), 4)
    abstention_signal  = sum(1 for g in groups if g["ABSTAIN"] > g["FOR"] and g["ABSTAIN"] > g["AGAINST"])
    total_for     = sum(g["FOR"]     for g in groups)
    total_against = sum(g["AGAINST"] for g in groups)
    dominant_bloc = "FOR" if total_for > total_against else ("AGAINST" if total_against > total_for else "TIED")

    return {
        "consensus_score":    consensus_score,
        "polarization_score": polarization_score,
        "abstention_signal":  abstention_signal,
        "dominant_bloc":      dominant_bloc,
    }


def generate_ai_insight(summary_dict: VoteSummary, topic: str) -> str:
    summary_list = [
        {"group": group, "FOR": counts["FOR"], "AGAINST": counts["AGAINST"], "ABSTAIN": counts["ABSTAIN"]}
        for group, counts in summary_dict.items()
    ]
    metrics = compute_vote_metrics(summary_list)

    prompt = f"""[INST]
YOU ARE A TEXT FORMATTER ONLY. DO NOT COMPUTE ANYTHING.
USE ONLY THE VALUES PROVIDED BELOW — COPY THEM VERBATIM.

TOPIC: {topic}
PRECOMPUTED VALUES:
- Groups: {metrics["groups"]}
- Ranking by FOR (high→low): {metrics["ranking_for"]}
- Highest FOR: {metrics["max_for"]}
- Lowest FOR: {metrics["min_for"]}
- Delta FOR: {metrics["delta_for"]}

OUTPUT FORMAT: BLOCS, RANKING_FOR, HIGHEST_FOR, LOWEST_FOR, DELTA_FOR, CLEAVAGE, EXECUTIVE_SUMMARY
COPY VALUES ONLY. NO CALCULATIONS. NO INTERPRETATION.
[/INST]"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        if "response" not in data:
            return "Error: Ollama response missing expected 'response' field."
        return validate_output(data["response"])
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Run `ollama serve` and `ollama pull mistral`."
    except requests.exceptions.Timeout:
        return "Error: Ollama did not respond within 180 seconds."
    except requests.exceptions.HTTPError as e:
        return f"Error: Ollama returned HTTP {e.response.status_code}."
    except ValueError:
        return "Error: Could not parse Ollama response as JSON."
```

---

### 6.9 `src/app.py`

**Purpose:** The Streamlit dashboard. This is the primary interface users interact with. Runs as a web app.

**Sections:**
1. **Demo Mode banner** — shown if `DEMO_MODE=true`
2. **KPI row** — Total Votes, Policy Topics, Political Groups, % FOR
3. **Global Vote Analytics** — bar charts + group ranking table
4. **Topic Analysis** — free-text search → voting breakdown + AI insight button
5. **Recent Political Changes** — three sub-sections:
   - Historical Insight (group behavior table, always shown)
   - Recent Change Analysis (metrics row: most changed group, topic, polarization change)
   - AI Summary (plain-English explanation from `explain_political_changes`)

**Caching strategy:** All data-loading and computation functions are wrapped with `@st.cache_data` so they do not re-run on every Streamlit interaction:
- `get_votes()` → `fetch_all_votes()`
- `get_historical_votes()` → `get_eu_votes()` (limited to 5000 rows in DEMO_MODE)
- `get_recent_votes(days=30)` → `load_recent_votes(30)`
- `get_cached_comparison(historical_df, recent_df)` → `compare_behavior(...)` (cached per unique DataFrame pair)

**Safe mode:** `get_recent_votes()` is called inside a `try/except`. If it throws, `recent_df` stays as an empty DataFrame and the section shows a calm `st.info` message instead of crashing.

**Demo mode behavior:**
- Historical dataset capped at 5,000 rows
- Ollama AI Insight call in Topic Analysis is skipped (replaced by `st.info`)
- AI Summary in Recent Political Changes is skipped (replaced by `st.info`)
- Historical Insight table and change metrics are still shown

```python
import os
import pandas as pd
import streamlit as st
from eu_api import fetch_all_votes
from analysis_agent import analyze_policy, generate_ai_insight
from eu_dataset_loader import get_eu_votes
from recent_data_loader import load_recent_votes
from political_comparison_engine import compare_behavior, compute_group_behavior
from political_ai_explainer import explain_political_changes

DEMO_MODE     = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")
_DEMO_ROW_LIMIT = 5000

st.set_page_config(page_title="EU Parliament Analytics Dashboard", layout="wide")
st.title("EU Parliament Analytics Dashboard")
st.caption("Analysis of European Parliament voting patterns with AI-generated insights.")

if DEMO_MODE:
    st.info("**Demo Mode** — dataset capped at 5,000 rows and Ollama AI calls are disabled.")

st.divider()


@st.cache_data
def get_votes() -> pd.DataFrame:
    return fetch_all_votes()

@st.cache_data
def get_historical_votes() -> pd.DataFrame:
    df = get_eu_votes()
    if DEMO_MODE and len(df) > _DEMO_ROW_LIMIT:
        df = df.tail(_DEMO_ROW_LIMIT).reset_index(drop=True)
    return df

@st.cache_data
def get_recent_votes(days: int = 30) -> pd.DataFrame:
    return load_recent_votes(days)

@st.cache_data
def get_cached_comparison(historical_df: pd.DataFrame, recent_df: pd.DataFrame) -> dict:
    return compare_behavior(historical_df, recent_df)


votes_df        = get_votes()
available_topics = sorted(votes_df["policy_topic"].dropna().unique().tolist())

# KPI row
total_votes = len(votes_df)
pct_for     = round(100 * (votes_df["vote"] == "FOR").sum() / total_votes, 1)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Votes",      total_votes)
k2.metric("Policy Topics",    votes_df["policy_topic"].nunique())
k3.metric("Political Groups", votes_df["political_group"].nunique())
k4.metric("FOR Votes",        f"{pct_for}%")

st.divider()

# Global Vote Analytics
st.header("Global Vote Analytics")
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Overall Vote Distribution")
    vote_counts = votes_df["vote"].value_counts().reindex(["FOR","AGAINST","ABSTAIN"]).fillna(0).rename("Votes")
    st.bar_chart(vote_counts)
with col_right:
    st.subheader("Total Votes by Political Group")
    group_counts = votes_df.groupby("political_group").size().sort_values(ascending=False).rename("Votes")
    st.bar_chart(group_counts)

st.subheader("Political Group Ranking")
ranking_df = votes_df.groupby(["political_group","vote"]).size().unstack(fill_value=0).reindex(columns=["FOR","AGAINST","ABSTAIN"],fill_value=0)
ranking_df["Total"] = ranking_df.sum(axis=1)
ranking_df = ranking_df.sort_values("Total", ascending=False)
ranking_df.index.name = "Political Group"
st.dataframe(ranking_df, use_container_width=True)

st.divider()

# Topic Analysis
st.header("Topic Analysis")
query = st.text_input("Search for a policy topic", placeholder="e.g. AI, migration, climate...")
topic = None
if query:
    matches = [t for t in available_topics if query.lower() in t.lower()]
    if not matches:
        st.warning(f"No topic found for '{query}'. Available: {', '.join(available_topics)}")
    elif len(matches) == 1:
        topic = matches[0]
        st.success(f"Matched: **{topic}**")
    else:
        topic = st.selectbox("Multiple matches — select one:", matches)

if topic and st.button("Analyze"):
    try:
        topic_summary = analyze_policy(votes_df, topic)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.subheader("Voting Summary")
    cols = st.columns(3)
    cols[0].markdown("**Political Group**")
    cols[1].markdown("**Votes**")
    cols[2].markdown("**Breakdown**")
    for group, counts in sorted(topic_summary.items()):
        total = sum(counts.values())
        c1, c2, c3 = st.columns(3)
        c1.write(group)
        c2.write(f"{total} votes")
        c3.write(f"FOR {counts['FOR']}  ·  AGAINST {counts['AGAINST']}  ·  ABSTAIN {counts['ABSTAIN']}")

    st.divider()
    st.subheader("Vote Distribution")
    chart_df = pd.DataFrame(topic_summary).T[["FOR","AGAINST","ABSTAIN"]]
    st.bar_chart(chart_df)

    st.divider()
    st.subheader("AI Insight")
    if DEMO_MODE:
        st.info("AI Insight is disabled in Demo Mode.")
    else:
        with st.spinner("Loading AI insight…"):
            insight = generate_ai_insight(topic_summary, topic)
        if insight.startswith("Error:"):
            st.warning(insight)
        else:
            st.write(insight)

st.divider()

# Recent Political Changes
st.header("Recent Political Changes")
st.caption("Compares voting behavior from the last 30 days against the full historical dataset.")

historical_df = get_historical_votes()

st.subheader("Historical Insight")
hist_behavior = compute_group_behavior(historical_df)
st.dataframe(hist_behavior.set_index("political_group"), use_container_width=True)

st.subheader("Recent Change Analysis")
recent_df = pd.DataFrame()
try:
    recent_df = get_recent_votes(days=30)
except Exception as exc:
    st.warning(f"Could not load recent vote data: {exc}")

if recent_df.empty:
    st.info("No recent vote data found. Add CSV files to data/recent/ or data/processed/ to enable change detection.")
else:
    try:
        comparison        = get_cached_comparison(historical_df, recent_df)
        comparison_summary = comparison.get("summary", {})
        mc_group   = comparison_summary.get("most_changed_group") or "—"
        mc_topic   = comparison_summary.get("most_changed_topic") or "—"
        pol_change = comparison_summary.get("overall_polarization_change")
        pol_label  = f"{pol_change:+.1f} pp" if pol_change is not None else "—"
        pol_delta_color = "normal" if pol_change is None or abs(pol_change) < 1.0 else ("inverse" if pol_change > 0 else "normal")

        m1, m2, m3 = st.columns(3)
        m1.metric("Most Changed Group", mc_group)
        m2.metric("Most Changed Topic", mc_topic)
        m3.metric("Polarization Change", pol_label, delta=pol_label, delta_color=pol_delta_color)

        st.subheader("AI Summary")
        if DEMO_MODE:
            st.info("AI Summary is disabled in Demo Mode.")
        else:
            explanation = explain_political_changes(comparison)
            st.write(explanation)

    except Exception as exc:
        st.warning(f"Could not compute recent changes: {exc}")
```

---

### 6.10 `src/prompts.py`

**Status:** Legacy file. Not used by the current pipeline. Retained because `requirements.txt` includes `langchain-core`.

```python
from langchain_core.prompts import ChatPromptTemplate

POLICY_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are an expert analyst specializing in EU policy and regulation."),
    ("human", "{user_input}"),
])

SUMMARY_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are an expert analyst specializing in EU policy and regulation. Summarize the following policy document concisely."),
    ("human", "{document}"),
])
```

---

### 6.11 `src/main.py`

**Status:** Legacy CLI. Still functional. Uses the old `data_loader.load_votes()` (not `eu_dataset_loader`). Useful for quick terminal-based testing without Streamlit.

```python
from data_loader import load_votes
from analysis_agent import analyze_policy, generate_ai_insight

def main() -> None:
    votes_df  = load_votes()
    available = sorted(votes_df["policy_topic"].unique().tolist())
    topic_lookup = {t.lower(): t for t in available}

    print("Available topics:")
    for topic in available:
        print(f"  • {topic}")

    while True:
        user_input = input("Topic > ").strip()
        if user_input.lower() == "exit":
            break
        canonical = topic_lookup.get(user_input.lower())
        if canonical is None:
            print(f"Topic not found: '{user_input}'")
            continue

        summary = analyze_policy(votes_df, canonical)
        insight = generate_ai_insight(summary, canonical)
        print(insight)

if __name__ == "__main__":
    main()
```

---

### 6.12 `scripts/load_real_votes.py`

**Purpose:** One-shot ingestion script that converts the HowTheyVote raw CSV dump into the project's standard schema and writes `data/processed/eu_votes_real.csv`.

**Input files required in `data/raw/real_votes/`:**
| File | Key columns |
|---|---|
| `member_votes.csv` | vote_id, member_id, position, country_code, group_code |
| `members.csv` | id, first_name, last_name |
| `groups.csv` | code, label |
| `votes.csv` | id, timestamp, procedure_title, display_title |
| `group_memberships.csv` | member_id, group_code, term, start_date, end_date (not currently used) |

**How it works:**
1. Loads the three small lookup tables (`members`, `groups`, `votes`) into Python dicts for O(1) lookup.
2. Streams `member_votes.csv` in chunks of 500,000 rows to stay under 2 GB RAM (the source file is ~490 MB).
3. For each chunk: maps `member_id → member_name`, `group_code → political_group label`, `vote_id → date + policy_topic`, `position → FOR/AGAINST/ABSTAIN`.
4. Drops rows missing `member_name`, `political_group`, or `vote`.
5. Writes to `data/processed/eu_votes_real.csv` incrementally (first chunk writes header, subsequent chunks append).

**Position mapping:**
```
FOR          → FOR
AGAINST      → AGAINST
ABSTENTION   → ABSTAIN
DID_NOT_VOTE → ABSTAIN
```

**Note on real data:** `policy_topic` in the real dataset comes from `procedure_title` (or `display_title` as fallback). These are raw parliamentary procedure names in multiple languages (e.g., "Mardi - demande du groupe GUE/NGL"), not the clean labels like "AI Act" used in the sample CSV. The topic-matching system in `eu_api.search_policy_topic` would need cleaning/mapping before the real dataset works well in the UI.

---

## 7. Module Dependency Graph

```
app.py
  ├── eu_api.py               → eu_dataset_loader.py → config.py
  ├── analysis_agent.py       (standalone, calls Ollama via HTTP)
  ├── eu_dataset_loader.py    → config.py
  ├── recent_data_loader.py   → config.py
  ├── political_comparison_engine.py  (pandas only, no imports from project)
  └── political_ai_explainer.py       (stdlib only, no imports from project)

main.py (legacy CLI)
  ├── data_loader.py          → config.py
  └── analysis_agent.py

scripts/load_real_votes.py
  └── config.py
```

---

## 8. Sample Data

**`data/raw/eu_votes_sample.csv`** — 32 rows, 6 topics, 6 groups, real MEP names:

```
member_name,political_group,policy_topic,vote,date
Axel Voss,EPP,AI Act,FOR,2024-03-13
Brando Benifei,S&D,AI Act,FOR,2024-03-13
Dragoș Tudorache,Renew,AI Act,FOR,2024-03-13
Kim Van Sparrentak,Greens/EFA,AI Act,FOR,2024-03-13
Annalisa Tardino,ID,AI Act,AGAINST,2024-03-13
Kosma Złotowski,ECR,AI Act,ABSTAIN,2024-03-13
Peter Liese,EPP,Climate Policy,AGAINST,2023-04-18
Mohammed Chahim,S&D,Climate Policy,FOR,2023-04-18
Pascal Canfin,Renew,Climate Policy,FOR,2023-04-18
Michael Bloss,Greens/EFA,Climate Policy,FOR,2023-04-18
Marco Zanni,ID,Climate Policy,AGAINST,2023-04-18
Bogdan Rzońca,ECR,Climate Policy,AGAINST,2023-04-18
Roberta Metsola,EPP,Migration Policy,FOR,2023-09-20
Birgit Sippel,S&D,Migration Policy,AGAINST,2023-09-20
Sophie in 't Veld,Renew,Migration Policy,AGAINST,2023-09-20
Erik Marquardt,Greens/EFA,Migration Policy,AGAINST,2023-09-20
Matteo Salvini,ID,Migration Policy,FOR,2023-09-20
Nicola Procaccini,ECR,Migration Policy,FOR,2023-09-20
Andreas Schwab,EPP,Digital Services Act,FOR,2022-07-05
Christel Schaldemose,S&D,Digital Services Act,FOR,2022-07-05
Dita Charanzová,Renew,Digital Services Act,FOR,2022-07-05
Alexandra Geese,Greens/EFA,Digital Services Act,FOR,2022-07-05
Ivan Štefanec,ECR,Digital Services Act,ABSTAIN,2022-07-05
Manfred Weber,EPP,Green Deal,AGAINST,2023-06-22
Iratxe García Pérez,S&D,Green Deal,FOR,2023-06-22
Nathalie Colin-Oesterlé,Renew,Green Deal,FOR,2023-06-22
Bas Eickhout,Greens/EFA,Green Deal,FOR,2023-06-22
Jordan Bardella,ID,Green Deal,AGAINST,2023-06-22
Bart Groothuis,Renew,Cybersecurity,FOR,2022-11-10
Maria Walsh,EPP,Cybersecurity,FOR,2022-11-10
Lukas Mandl,ECR,Cybersecurity,FOR,2022-11-10
Hannah Neumann,Greens/EFA,Cybersecurity,ABSTAIN,2022-11-10
```

---

## 9. Current Status

### Working
- Full Streamlit dashboard (KPIs, charts, topic search, group ranking)
- CSV-based data loading with 3-level fallback chain
- HowTheyVote ingestion pipeline (`scripts/load_real_votes.py`)
- Historical vs recent comparison engine (pure pandas)
- Plain-English AI explainer (no LLM required)
- Ollama/mistral AI insight for topic analysis
- Demo Mode (env var flag)
- Safe Mode (no crash when recent data is missing)

### Not yet working / known gaps
1. **Recent data folder is empty.** `data/recent/` does not exist. The "Recent Change Analysis" section in the dashboard always shows the "no data" info message. To test it: create `data/recent/` and drop a CSV there with the same 5-column schema and recent dates.
2. **Real data topic names are not clean.** The `eu_votes_real.csv` produced by `load_real_votes.py` has raw procedure titles (multilingual, long, procedural) not the clean labels like "AI Act". Topic search won't find useful matches.
3. **Claude integration is commented out.** The stub in `analysis_agent.py` works but is disabled. Uncomment 3 lines and provide `ANTHROPIC_API_KEY` to switch from Ollama to Claude.
4. **`prompts.py` is unused.** Legacy file, kept for potential future use.
5. **`main.py` uses `data_loader` not `eu_dataset_loader`.** Minor inconsistency. CLI works, but it won't pick up `eu_votes_real.csv` as the real-data source the way the Streamlit app does.

---

## 10. Planned Next Steps

1. **Wire Claude API** — replace Ollama in `analysis_agent.generate_ai_insight()` using the commented-out stub. Requires `ANTHROPIC_API_KEY` in `.env`.
2. **Live EP Open Data Portal** — replace the body of `eu_api.fetch_all_votes()` with a call to `https://data.europarl.europa.eu/api/v2/votes`. The integration point is documented in `eu_api.py`.
3. **Clean real topic names** — add a normalization/mapping step in `load_real_votes.py` that maps raw procedure titles to canonical topic labels (or build a classifier using Claude).
4. **Populate `data/recent/`** — add automation to fetch recent votes daily and drop them in `data/recent/` so the comparison section activates.
5. **Deploy** — Streamlit Cloud or Docker container.

---

## 11. Key Design Rules (Do Not Break)

1. **Universal schema.** Every DataFrame that crosses a module boundary must have exactly these 5 columns: `member_name`, `political_group`, `policy_topic`, `vote`, `date`. Never add or rename.
2. **`get_mock_votes()` must stay** in `data_loader.py` — it is the emergency fallback for the legacy CLI path.
3. **No computation in `political_ai_explainer.py`.** It reads numbers from the input dict and formats them. Never add pandas or math there.
4. **No LLM calls in `political_comparison_engine.py` or `recent_data_loader.py`.** These are pure data layers.
5. **`eu_api.py` is the only public gate** to vote data for `app.py`. Do not import `eu_dataset_loader` directly in `app.py` (it currently does for the `get_historical_votes()` function — this is acceptable but the pattern should not spread further).
6. **`@st.cache_data` on all data loaders and computations** in `app.py`. Never call `get_eu_votes()` bare in render code.
7. **`data_loader.py` is legacy** — do not add new features there. New features go in `eu_dataset_loader.py`.

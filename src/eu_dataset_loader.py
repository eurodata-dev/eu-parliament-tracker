"""eu_dataset_loader.py — EU Parliament voting data, loaded by year range."""
from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd
from config import settings

logger = logging.getLogger(__name__)
SCHEMA: list[str] = ["member_name", "political_group", "policy_topic", "vote", "date"]

_FALLBACK_RECORDS: list[dict] = [
    {"member_name": "Dragos Tudorache",     "political_group": "Renew",      "policy_topic": "AI Act",               "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Brando Benifei",       "political_group": "S&D",        "policy_topic": "AI Act",               "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Peter Kofod",          "political_group": "ID",         "policy_topic": "AI Act",               "vote": "AGAINST", "date": "2024-03-13"},
    {"member_name": "Mohammed Chahim",      "political_group": "S&D",        "policy_topic": "Climate Policy",       "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Bas Eickhout",         "political_group": "Greens/EFA", "policy_topic": "Climate Policy",       "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Alexandr Vondra",      "political_group": "ECR",        "policy_topic": "Climate Policy",       "vote": "AGAINST", "date": "2023-06-22"},
    {"member_name": "Roberta Metsola",      "political_group": "EPP",        "policy_topic": "Migration Policy",     "vote": "FOR",     "date": "2024-04-10"},
    {"member_name": "Tineke Strik",         "political_group": "Greens/EFA", "policy_topic": "Migration Policy",     "vote": "AGAINST", "date": "2024-04-10"},
]

BY_YEAR_DIR = "by_year"
ALL_YEARS   = list(range(2019, 2027))
DEFAULT_YEARS = [2024, 2025, 2026]  # default window at startup


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("member_name", "political_group", "policy_topic", "vote"):
        df[col] = df[col].fillna("").astype("category")
    return df


def get_available_years() -> list[int]:
    """Return which years have parquet files."""
    by_year = Path(settings.DATA_DIR) / "processed" / BY_YEAR_DIR
    if not by_year.exists():
        return []
    return sorted([
        int(p.stem.replace("eu_votes_", ""))
        for p in by_year.glob("eu_votes_*.parquet")
    ])


def get_eu_votes(years: list[int] | None = None) -> pd.DataFrame:
    """Load votes for the given years (defaults to recent 3 years).

    Falls back to the flat parquet, then CSV, then hardcoded records.
    """
    available = get_available_years()

    # --- yearly parquets available ---
    if available:
        if years is None:
            # Use most recent 3 available years as default
            years = sorted(available)[-3:]
        years_to_load = [y for y in years if y in available]
        if not years_to_load:
            years_to_load = sorted(available)[-3:]

        by_year = Path(settings.DATA_DIR) / "processed" / BY_YEAR_DIR
        parts = []
        for y in years_to_load:
            p = by_year / f"eu_votes_{y}.parquet"
            df_y = pd.read_parquet(p, columns=SCHEMA, engine="pyarrow")
            parts.append(df_y)
        df = pd.concat(parts, ignore_index=True)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        logger.info("Loaded %d rows for years %s", len(df), years_to_load)
        print(f"Loaded {len(df):,} rows for years {years_to_load}")
        return _clean(df)

    # --- flat parquet fallback ---
    flat = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    if flat.exists():
        df = pd.read_parquet(flat, columns=SCHEMA, engine="pyarrow")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        print(f"Loaded {len(df):,} rows from flat parquet")
        return _clean(df)

    # --- CSV fallback ---
    csv_path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, usecols=SCHEMA)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return _clean(df)

    # --- hardcoded fallback ---
    df = pd.DataFrame(_FALLBACK_RECORDS)
    df["date"] = pd.to_datetime(df["date"])
    return _clean(df[SCHEMA])

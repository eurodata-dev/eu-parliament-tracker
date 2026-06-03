"""
eu_dataset_loader.py — EU Parliament voting data ingestion layer.

Source priority (highest -> lowest):
  1. data/processed/eu_votes_real.parquet  -- fastest, produced by load_real_votes.py
  2. data/processed/eu_votes_real.csv      -- CSV fallback
  3. data/raw/eu_votes_sample.csv          -- small demo dataset
  4. hardcoded 12-record fallback          -- offline / CI
"""

from __future__ import annotations

import logging
import os
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
    {"member_name": "Dragos Tudorache",     "political_group": "Renew",      "policy_topic": "AI Act",               "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Brando Benifei",       "political_group": "S&D",        "policy_topic": "AI Act",               "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Peter Kofod",          "political_group": "ID",         "policy_topic": "AI Act",               "vote": "AGAINST", "date": "2024-03-13"},
    {"member_name": "Mohammed Chahim",      "political_group": "S&D",        "policy_topic": "Climate Policy",       "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Bas Eickhout",         "political_group": "Greens/EFA", "policy_topic": "Climate Policy",       "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Alexandr Vondra",      "political_group": "ECR",        "policy_topic": "Climate Policy",       "vote": "AGAINST", "date": "2023-06-22"},
    {"member_name": "Christel Schaldemose", "political_group": "S&D",        "policy_topic": "Digital Services Act", "vote": "FOR",     "date": "2022-07-05"},
    {"member_name": "Andreas Schwab",       "political_group": "EPP",        "policy_topic": "Digital Services Act", "vote": "FOR",     "date": "2022-07-05"},
    {"member_name": "Marcel de Graaff",     "political_group": "ID",         "policy_topic": "Digital Services Act", "vote": "AGAINST", "date": "2022-07-05"},
    {"member_name": "Roberta Metsola",      "political_group": "EPP",        "policy_topic": "Migration Policy",     "vote": "FOR",     "date": "2024-04-10"},
    {"member_name": "Tineke Strik",         "political_group": "Greens/EFA", "policy_topic": "Migration Policy",     "vote": "AGAINST", "date": "2024-04-10"},
    {"member_name": "Fabrice Leggeri",      "political_group": "ID",         "policy_topic": "Migration Policy",     "vote": "ABSTAIN", "date": "2024-04-10"},
]

# Max rows to load — keeps memory under 500MB on Streamlit Cloud free tier
MAX_ROWS = 500_000


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("member_name", "political_group", "policy_topic", "vote"):
        df[col] = df[col].fillna("").astype("category")
    return df


def _load_from_parquet() -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    # Use pyarrow engine and load only needed columns to save memory
    df = pd.read_parquet(path, columns=SCHEMA, engine="pyarrow")
    # Deduplicate first
    df = df.drop_duplicates()
    # Cap rows if still too large
    if len(df) > MAX_ROWS:
        logger.warning("Parquet has %d rows after dedup — sampling to %d", len(df), MAX_ROWS)
        df = df.sample(n=MAX_ROWS, random_state=42)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    logger.info("Loaded %d rows from parquet (%d unique topics)", len(df), df["policy_topic"].nunique())
    return _clean(df[SCHEMA])


def _load_from_real_votes() -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    df = pd.read_csv(path, usecols=SCHEMA)
    df = df.drop_duplicates()
    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, random_state=42)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    logger.info("Loaded %d rows from real CSV", len(df))
    return _clean(df[SCHEMA])


def _load_from_csv() -> pd.DataFrame:
    csv_path = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    logger.info("Loaded %d vote records from sample CSV (%s)", len(df), csv_path)
    return _clean(df[SCHEMA])


def _load_fallback() -> pd.DataFrame:
    logger.warning("No CSV found — using hardcoded fallback dataset (%d records).", len(_FALLBACK_RECORDS))
    df = pd.DataFrame(_FALLBACK_RECORDS)
    df["date"] = pd.to_datetime(df["date"])
    return _clean(df[SCHEMA])


def get_eu_votes() -> pd.DataFrame:
    """Return a DataFrame of EU Parliament voting records.

    Source priority:
        1. data/processed/eu_votes_real.parquet  (fastest)
        2. data/processed/eu_votes_real.csv
        3. data/raw/eu_votes_sample.csv
        4. hardcoded 12-record fallback
    """
    parquet_path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    real_path    = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    sample_path  = Path(settings.DATA_DIR) / "raw"       / "eu_votes_sample.csv"

    if parquet_path.exists():
        df = _load_from_parquet()
    elif real_path.exists():
        df = _load_from_real_votes()
    elif sample_path.exists():
        df = _load_from_csv()
    else:
        df = _load_fallback()

    print(f"Loaded {len(df):,} rows (2019-2026)")
    return df

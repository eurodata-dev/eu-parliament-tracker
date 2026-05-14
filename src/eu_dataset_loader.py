"""
eu_dataset_loader.py — EU Parliament voting data ingestion layer.

Source priority (highest → lowest):
  1. data/processed/eu_votes_real.parquet  — fastest, produced by load_real_votes.py
  2. data/processed/eu_votes_real.csv      — CSV fallback
  3. data/raw/eu_votes_sample.csv          — small demo dataset
  4. hardcoded 12-record fallback          — offline / CI
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


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("member_name", "political_group", "policy_topic", "vote"):
        df[col] = df[col].fillna("").astype(str)
    return df


def _load_from_parquet() -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    unique_topics = df["policy_topic"].dropna().nunique()
    logger.info(
        "Loaded %d vote records from parquet (%s) — %d unique topic(s)",
        len(df), path, unique_topics,
    )
    return _clean(df[SCHEMA])


def _load_from_real_votes() -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    unique_topics = df["policy_topic"].dropna().nunique()
    logger.info(
        "Loaded %d vote records from real dataset (%s) — %d unique topic(s)",
        len(df), path, unique_topics,
    )
    return _clean(df[SCHEMA])


def _load_from_csv() -> pd.DataFrame:
    csv_path = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    logger.info("Loaded %d vote records from sample CSV (%s)", len(df), csv_path)
    return _clean(df[SCHEMA])


def _load_fallback() -> pd.DataFrame:
    logger.warning(
        "No CSV found — using hardcoded fallback dataset (%d records).",
        len(_FALLBACK_RECORDS),
    )
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

    # DEV/DEMO mode: sample down to 50k rows for fast iteration
    env = settings.ENV
    demo_mode = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")
    if env == "development" or demo_mode:
        n = min(50_000, len(df))
        df = df.sample(n=n, random_state=42)
        print(f"DEV MODE: sampled {n:,} rows from full dataset")

    return df

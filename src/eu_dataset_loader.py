"""eu_dataset_loader.py — EU Parliament voting data ingestion layer."""

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
    {"member_name": "Christel Schaldemose", "political_group": "S&D",        "policy_topic": "Digital Services Act", "vote": "FOR",     "date": "2022-07-05"},
    {"member_name": "Andreas Schwab",       "political_group": "EPP",        "policy_topic": "Digital Services Act", "vote": "FOR",     "date": "2022-07-05"},
    {"member_name": "Marcel de Graaff",     "political_group": "ID",         "policy_topic": "Digital Services Act", "vote": "AGAINST", "date": "2022-07-05"},
    {"member_name": "Roberta Metsola",      "political_group": "EPP",        "policy_topic": "Migration Policy",     "vote": "FOR",     "date": "2024-04-10"},
    {"member_name": "Tineke Strik",         "political_group": "Greens/EFA", "policy_topic": "Migration Policy",     "vote": "AGAINST", "date": "2024-04-10"},
    {"member_name": "Fabrice Leggeri",      "political_group": "ID",         "policy_topic": "Migration Policy",     "vote": "ABSTAIN", "date": "2024-04-10"},
]

MAX_ROWS = 300_000


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("member_name", "political_group", "policy_topic", "vote"):
        df[col] = df[col].fillna("").astype("category")
    return df


def _load_from_parquet() -> pd.DataFrame:
    import pyarrow.parquet as pq
    import pyarrow as pa
    path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    pf = pq.ParquetFile(str(path))
    num_rg = pf.metadata.num_row_groups
    logger.info("Parquet has %d row groups, %d total rows", num_rg, pf.metadata.num_rows)
    # Read row groups one at a time until we have enough rows
    tables = []
    rows_so_far = 0
    for i in range(num_rg):
        rg = pf.read_row_group(i, columns=SCHEMA)
        tables.append(rg)
        rows_so_far += rg.num_rows
        if rows_so_far >= MAX_ROWS:
            break
    table = pa.concat_tables(tables)
    df = table.to_pandas()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.drop_duplicates()
    logger.info("Loaded %d rows from parquet (%d unique topics)", len(df), df["policy_topic"].nunique())
    return _clean(df)


def _load_from_csv() -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    df = pd.read_csv(path, usecols=SCHEMA)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.drop_duplicates()
    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, random_state=42)
    return _clean(df)


def _load_from_sample() -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return _clean(df[SCHEMA])


def _load_fallback() -> pd.DataFrame:
    df = pd.DataFrame(_FALLBACK_RECORDS)
    df["date"] = pd.to_datetime(df["date"])
    return _clean(df[SCHEMA])


def get_eu_votes() -> pd.DataFrame:
    parquet_path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    csv_path     = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    sample_path  = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"

    if parquet_path.exists():
        df = _load_from_parquet()
    elif csv_path.exists():
        df = _load_from_csv()
    elif sample_path.exists():
        df = _load_from_sample()
    else:
        df = _load_fallback()

    print(f"Loaded {len(df):,} rows")
    return df

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone

from config import settings

SCHEMA_COLUMNS = ["member_name", "political_group", "policy_topic", "vote", "date"]

_RECENT_DIR = Path(settings.DATA_DIR) / "recent"
_PROCESSED_DIR = Path(settings.DATA_DIR) / "processed"


def _load_recent_csv_files() -> pd.DataFrame:
    """Load and concatenate all CSV files from the recent or processed data directory."""
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

    Reads from data/recent/ (preferred) or data/processed/ (fallback).
    Returns an empty DataFrame with the correct schema if no data is found
    or no rows fall within the requested window.

    Args:
        days: Number of days back from today to include. Default is 30.

    Returns:
        pd.DataFrame with columns: member_name, political_group,
        policy_topic, vote, date.
    """
    df = _load_recent_csv_files()

    if df.empty:
        return df

    # Keep only recognised schema columns that are present; drop the rest.
    present = [col for col in SCHEMA_COLUMNS if col in df.columns]
    df = df[present].copy()

    # Ensure all schema columns exist (fill any missing ones with pd.NA).
    for col in SCHEMA_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    # Parse dates - coerce unparseable values to NaT instead of raising.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop rows where date could not be parsed.
    df = df.dropna(subset=["date"])

    if df.empty:
        return df[SCHEMA_COLUMNS]

    # Normalise to UTC-naive for comparison.
    if df["date"].dt.tz is not None:
        df["date"] = df["date"].dt.tz_convert("UTC").dt.tz_localize(None)

    cutoff = datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    df = df[df["date"] >= cutoff].copy()

    return df[SCHEMA_COLUMNS].reset_index(drop=True)

"""
scripts/load_real_votes.py — HowTheyVote dataset ingestion pipeline.

HowTheyVote schema (data/raw/real_votes/):
    member_votes.csv   — vote_id, member_id, position, country_code, group_code
    votes.csv          — id, timestamp, display_title, procedure_title, ...
    members.csv        — id, first_name, last_name, ...
    groups.csv         — code, label, short_label, ...
    group_memberships.csv — member_id, group_code, term, start_date, end_date

Join strategy:
    member_votes  LEFT JOIN  members  ON member_id = members.id
                  LEFT JOIN  groups   ON group_code = groups.code
                  LEFT JOIN  votes    ON vote_id    = votes.id

Output schema (data/processed/eu_votes_real.csv):
    member_name, political_group, policy_topic, vote, date

Usage (run from project root):
    python scripts/load_real_votes.py
"""

import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

SCHEMA: list[str] = ["member_name", "political_group", "policy_topic", "vote", "date"]
_REQUIRED: list[str] = ["member_name", "political_group", "vote"]
_VALID_VOTES: set[str] = {"FOR", "AGAINST", "ABSTAIN"}

# HowTheyVote position values → canonical vote label
_POSITION_MAP: dict[str, str] = {
    "FOR":          "FOR",
    "AGAINST":      "AGAINST",
    "ABSTENTION":   "ABSTAIN",
    "DID_NOT_VOTE": "ABSTAIN",
}

# Full EP group names → short labels used throughout the project
_GROUP_LABEL_MAP: dict[str, str] = {
    "Progressive Alliance of Socialists and Democrats": "S&D",
    "Group of the European People's Party":             "EPP",
    "Renew Europe Group":                               "Renew",
    "Group of the Greens/European Free Alliance":       "Greens/EFA",
    "European Conservatives and Reformists Group":      "ECR",
    "Identity and Democracy Group":                     "ID",
    "The Left group in the European Parliament":        "The Left",
    "Non-attached Members":                             "NI",
}

# Rows per iteration — keeps peak RAM well under 2 GB for a 490 MB source file
CHUNK_SIZE = 500_000


# ---------------------------------------------------------------------------
# Lookup-table builder
# ---------------------------------------------------------------------------

def _build_lookups(raw_dir: Path) -> tuple[dict, dict, dict, dict]:
    """Load the three small reference tables into O(1) lookup dicts.

    Returns:
        member_map  — member_id  → "First Last"
        group_map   — group_code → human-readable label
        date_map    — vote_id    → ISO timestamp string
        topic_map   — vote_id    → policy topic string
    """
    # members.csv  (≈1 274 rows)
    members = pd.read_csv(
        raw_dir / "members.csv",
        usecols=["id", "first_name", "last_name"],
        dtype={"id": int, "first_name": str, "last_name": str},
    )
    members["member_name"] = (
        members["first_name"].str.strip() + " " + members["last_name"].str.strip()
    )
    member_map: dict[int, str] = members.set_index("id")["member_name"].to_dict()
    logger.info("Lookup: %d members loaded", len(member_map))

    # groups.csv  (11 rows)
    groups = pd.read_csv(raw_dir / "groups.csv", usecols=["code", "label"])
    group_map: dict[str, str] = groups.set_index("code")["label"].to_dict()
    logger.info("Lookup: %d political groups loaded: %s", len(group_map), sorted(group_map.keys()))

    # votes.csv  (≈24 224 rows)
    votes = pd.read_csv(
        raw_dir / "votes.csv",
        usecols=["id", "timestamp", "procedure_title", "display_title"],
        dtype={"id": int},
        low_memory=False,
    )
    # Use procedure_title as primary topic; fall back to display_title
    votes["policy_topic"] = votes["procedure_title"].fillna(votes["display_title"])
    date_map: dict[int, str]  = votes.set_index("id")["timestamp"].to_dict()
    topic_map: dict[int, str] = votes.set_index("id")["policy_topic"].to_dict()
    logger.info("Lookup: %d vote-level records loaded", len(date_map))

    return member_map, group_map, date_map, topic_map


# ---------------------------------------------------------------------------
# Chunked processor
# ---------------------------------------------------------------------------

def _process_chunk(
    chunk: pd.DataFrame,
    member_map: dict,
    group_map: dict,
    date_map: dict,
    topic_map: dict,
) -> tuple[pd.DataFrame, int, int]:
    """Apply lookups and validation to one chunk of member_votes.

    Returns:
        (result_df, rows_kept, rows_skipped)
    """
    raw_count = len(chunk)

    # Vectorised dict lookups — much faster than merge for small dicts
    chunk = chunk.copy()
    chunk["member_name"]    = chunk["member_id"].map(member_map)
    chunk["political_group"] = chunk["group_code"].map(group_map)
    chunk["vote"]           = chunk["position"].map(_POSITION_MAP)
    chunk["date"]           = chunk["vote_id"].map(date_map)
    chunk["policy_topic"]   = chunk["vote_id"].map(topic_map)

    result = chunk[SCHEMA].copy()

    # Filter to term 9 and 10 only (2019 onward)
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result[result["date"] >= "2019-01-01"]

    # Normalize group names; keep raw procedure titles, just strip whitespace
    result["political_group"] = result["political_group"].map(
        lambda x: _GROUP_LABEL_MAP.get(x, x)
    )
    result["policy_topic"] = result["policy_topic"].str.strip()
    result = result[result["policy_topic"].notna() & (result["policy_topic"] != "")]

    # Drop rows where any required field is missing or vote is unrecognised
    result = result.dropna(subset=_REQUIRED)
    result = result[result["vote"].isin(_VALID_VOTES)]

    kept    = len(result)
    skipped = raw_count - kept
    return result, kept, skipped


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    data_dir = Path(settings.DATA_DIR)
    raw_dir  = data_dir / "raw" / "real_votes"
    out_dir  = data_dir / "processed"
    out_path = out_dir / "eu_votes_real.csv"

    out_dir.mkdir(parents=True, exist_ok=True)

    member_votes_path = raw_dir / "member_votes.csv"
    if not member_votes_path.exists():
        logger.error("member_votes.csv not found in %s", raw_dir)
        return

    # ── Phase 1: build lookup dicts from small reference tables ───────────
    logger.info("=" * 60)
    logger.info("Phase 1 — Loading lookup tables")
    logger.info("=" * 60)
    member_map, group_map, date_map, topic_map = _build_lookups(raw_dir)

    # ── Phase 2: stream-process the large member_votes file ───────────────
    logger.info("=" * 60)
    logger.info("Phase 2 — Processing member_votes.csv in chunks of %d", CHUNK_SIZE)
    logger.info("=" * 60)

    # Fast row-count estimate (byte scan, no CSV parse overhead)
    with open(member_votes_path, "rb") as fh:
        total_raw_rows = sum(1 for _ in fh) - 1  # subtract header
    total_chunks = (total_raw_rows + CHUNK_SIZE - 1) // CHUNK_SIZE
    logger.info("Source rows: %d  |  Estimated chunks: %d", total_raw_rows, total_chunks)

    # Accumulators for validation stats
    total_kept    = 0
    total_skipped = 0
    vote_counts: dict[str, int] = {"FOR": 0, "AGAINST": 0, "ABSTAIN": 0}
    seen_groups: set[str] = set()
    seen_topics: set[str] = set()
    first_chunk = True

    for chunk_idx, raw_chunk in enumerate(
        pd.read_csv(
            member_votes_path,
            chunksize=CHUNK_SIZE,
            dtype={"vote_id": int, "member_id": int, "position": str,
                   "country_code": str, "group_code": str},
        ),
        start=1,
    ):
        result, kept, skipped = _process_chunk(
            raw_chunk, member_map, group_map, date_map, topic_map
        )

        result.to_csv(
            out_path,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )
        first_chunk = False

        total_kept    += kept
        total_skipped += skipped
        for label in _VALID_VOTES:
            vote_counts[label] += (result["vote"] == label).sum()
        seen_groups.update(result["political_group"].dropna().unique())
        seen_topics.update(result["policy_topic"].dropna().unique())

        pct_done = chunk_idx / total_chunks * 100
        logger.info(
            "Chunk %4d / %d  [%5.1f%%]  kept=%7d  skipped=%6d  total_written=%9d",
            chunk_idx, total_chunks, pct_done, kept, skipped, total_kept,
        )

    # ── Phase 3: validation report ─────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("Phase 3 — Validation report")
    logger.info("=" * 60)
    logger.info("Rows written       : %d", total_kept)
    logger.info("Rows skipped       : %d", total_skipped)
    logger.info("Skip rate          : %.2f%%", total_skipped / max(total_raw_rows, 1) * 100)
    logger.info("Unique MEPs        : (see output file)")
    logger.info("Unique groups      : %d", len(seen_groups))
    logger.info("Unique topics      : %d", len(seen_topics))
    logger.info("Vote distribution  :")
    for label in ("FOR", "AGAINST", "ABSTAIN"):
        pct = vote_counts[label] / max(total_kept, 1) * 100
        logger.info("  %-10s  %9d  (%.1f%%)", label, vote_counts[label], pct)
    logger.info("Output written to  : %s", out_path)
    logger.info("=" * 60)

    if total_kept == 0:
        logger.error("FATAL: zero rows written — check lookup tables and source file paths.")
    else:
        logger.info("SUCCESS — dataset ready for eu_dataset_loader.py")
        # Write parquet (read back the CSV we wrote in chunks)
        parquet_path = out_dir / "eu_votes_real.parquet"
        logger.info("Writing parquet file from %d rows...", total_kept)
        df_parquet = pd.read_csv(out_path)
        df_parquet.to_parquet(parquet_path, index=False)
        logger.info("Parquet written to : %s", parquet_path)


if __name__ == "__main__":
    run()

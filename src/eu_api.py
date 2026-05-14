"""
eu_api.py — EU Parliament data access layer.

Single point of contact between the application and EU Parliament voting data.
Its public interface is intentionally stable: when the data source changes
(CSV → bulk download → SPARQL), only eu_dataset_loader.py changes — callers
(app.py, analysis_agent.py) stay untouched.

Data flow:
    caller → eu_api.py → eu_dataset_loader.get_eu_votes() → CSV / EP Open Data
"""

from __future__ import annotations

import logging

import pandas as pd

import ep_live_fetcher
from eu_dataset_loader import SCHEMA, get_eu_votes

logger = logging.getLogger(__name__)

_EXPECTED_COLUMNS: list[str] = SCHEMA


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return text.strip().lower()


def _available_topics(votes_df: pd.DataFrame) -> list[str]:
    return sorted(votes_df["policy_topic"].unique().tolist())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search_policy_topic(query: str) -> str | None:
    """Resolve a free-text query to the closest known policy topic.

    Three-pass matching, most to least strict:
        1. Exact match (case-insensitive).
        2. Substring — topic contains query, or query contains topic.
        3. Word-overlap — any query word appears in a topic name.

    Returns the exact policy_topic label, or None if nothing matches.
    When the dataset grows richer, replace these passes with a proper
    text-search filter in eu_dataset_loader (e.g. SPARQL FILTER CONTAINS).
    """
    if not query or not query.strip():
        return None

    votes_df = get_eu_votes()
    topics = _available_topics(votes_df)
    q = _normalize(query)

    # Pass 1 — exact
    for topic in topics:
        if _normalize(topic) == q:
            logger.info("Topic matched (exact): %r", topic)
            return topic

    # Pass 2 — substring
    substring_matches = [
        t for t in topics
        if q in _normalize(t) or _normalize(t) in q
    ]
    if len(substring_matches) == 1:
        logger.info("Topic matched (substring): %r", substring_matches[0])
        return substring_matches[0]
    if len(substring_matches) > 1:
        best = min(substring_matches, key=len)
        logger.info("Topic matched (substring, shortest of %d): %r", len(substring_matches), best)
        return best

    # Pass 3 — word-overlap
    query_words = set(q.split())
    word_matches = [t for t in topics if query_words & set(_normalize(t).split())]
    if word_matches:
        best = min(word_matches, key=len)
        logger.info("Topic matched (word-overlap): %r", best)
        return best

    logger.warning("No topic matched for query: %r", query)
    return None


def fetch_all_votes() -> pd.DataFrame:
    """Return the full voting dataset — no topic filter.

    Attempts to refresh data/recent/ via the EP live API before returning
    historical data. If the live fetch fails for any reason the error is logged
    and the function continues normally — the app never crashes because of it.

    Used by app.py for global KPIs and charts.
    """
    try:
        ep_live_fetcher.run()
    except Exception as exc:
        logger.warning("EP live fetch skipped: %s", exc)

    return get_eu_votes()


def fetch_eu_votes(query: str) -> pd.DataFrame:
    """Return voting records matching a free-text policy topic query.

    Resolves the query to a known topic via search_policy_topic(), then
    filters the full dataset. Returns an empty DataFrame (correct schema)
    if no topic matches.
    """
    topic = search_policy_topic(query)
    if topic is None:
        return pd.DataFrame(columns=_EXPECTED_COLUMNS)

    votes_df = get_eu_votes()
    return votes_df[votes_df["policy_topic"] == topic].reset_index(drop=True)

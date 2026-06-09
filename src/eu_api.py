# eu_api.py
# Handles all data fetching for the app. Everything goes through here
# so if the data source ever changes, only this file needs updating.

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
    """Try to match a user's search query to a known policy topic.

    Does three passes: exact match first, then substring, then word overlap.
    Returns None if nothing is found.
    """
    if not query or not query.strip():
        return None

    votes_df = get_eu_votes()
    topics = _available_topics(votes_df)
    q = _normalize(query)

    # exact match
    for topic in topics:
        if _normalize(topic) == q:
            logger.info("Topic matched (exact): %r", topic)
            return topic

    # substring match
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

    # word overlap as last resort
    query_words = set(q.split())
    word_matches = [t for t in topics if query_words & set(_normalize(t).split())]
    if word_matches:
        best = min(word_matches, key=len)
        logger.info("Topic matched (word-overlap): %r", best)
        return best

    logger.warning("No topic matched for query: %r", query)
    return None


def fetch_all_votes() -> pd.DataFrame:
    """Returns the full vote dataset. Used for global stats and charts."""
    return get_eu_votes()


def fetch_eu_votes(query: str) -> pd.DataFrame:
    """Returns votes filtered by a search query. Empty DataFrame if no match."""
    topic = search_policy_topic(query)
    if topic is None:
        return pd.DataFrame(columns=_EXPECTED_COLUMNS)

    votes_df = get_eu_votes()
    return votes_df[votes_df["policy_topic"] == topic].reset_index(drop=True)

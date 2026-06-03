import logging
import statistics
from collections import Counter

import requests
import pandas as pd

from config import settings

# Nested vote counts keyed by political group.
# Shape: {"EPP": {"FOR": 2, "AGAINST": 1, "ABSTAIN": 0}, ...}
VoteSummary = dict[str, dict[str, int]]

logger = logging.getLogger(__name__)

_VOTE_LABELS = ["FOR", "AGAINST", "ABSTAIN"]


def build_summary(votes_df: pd.DataFrame) -> VoteSummary:
    """Aggregate a votes DataFrame into a per-group vote-count dictionary.

    Args:
        votes_df: DataFrame with at minimum columns ``political_group`` and
            ``vote`` (values: FOR | AGAINST | ABSTAIN).

    Returns:Donc
        Nested dict mapping each political group to its vote counts, e.g.::

            {
                "EPP":        {"FOR": 2, "AGAINST": 1, "ABSTAIN": 0},
                "Greens/EFA": {"FOR": 1, "AGAINST": 0, "ABSTAIN": 0},
            }
    """
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
    """Filter votes by policy topic and return a per-group vote summary.

    Args:
        votes_df: Full DataFrame of voting records (all topics).
        topic:    Exact ``policy_topic`` value to analyse, e.g. ``"AI Act"``.

    Returns:
        VoteSummary for the requested topic only.

    Raises:
        ValueError: If ``topic`` is not present in the DataFrame.
    """
    filtered = votes_df[votes_df["policy_topic"] == topic]
    if filtered.empty:
        raise ValueError(
            f"No voting records found for topic '{topic}'. "
            f"Available topics: {sorted(votes_df['policy_topic'].unique().tolist())}"
        )
    return build_summary(filtered)


def validate_output(text: str) -> str:
    """Basic sanity check on LLM output — only reject clearly broken responses."""
    if not text or len(text.strip()) < 20:
        return "API_ERROR"
    return text


def compute_vote_metrics(summary_list: list[dict]) -> dict:
    """Compute all vote statistics in pure Python — deterministic, no LLM involved.

    Enriches each group entry with derived fields, then computes dataset-level
    rankings and extremes from the enriched data.

    Per-group derived fields:
        TOTAL         = FOR + AGAINST + ABSTAIN
        PARTICIPATION = FOR + AGAINST  (excludes abstentions)
        FOR_RATIO     = FOR / TOTAL    (0.0 if TOTAL == 0)
        AGAINST_RATIO = AGAINST / TOTAL (0.0 if TOTAL == 0)

    Args:
        summary_list: List of dicts with keys group, FOR, AGAINST, ABSTAIN.

    Returns:
        Dict with enriched groups and precomputed ranking, max/min, delta values.
    """
    enriched = []
    for row in summary_list:
        total = row["FOR"] + row["AGAINST"] + row["ABSTAIN"]
        enriched.append({
            **row,
            "TOTAL": total,
            "PARTICIPATION": row["FOR"] + row["AGAINST"],
            "FOR_RATIO": round(row["FOR"] / total, 4) if total else 0.0,
            "AGAINST_RATIO": round(row["AGAINST"] / total, 4) if total else 0.0,
        })

    ranking_for = sorted(enriched, key=lambda r: r["FOR"], reverse=True)
    ranking_against = sorted(enriched, key=lambda r: r["AGAINST"], reverse=True)
    max_for = ranking_for[0]
    min_for = ranking_for[-1]
    return {
        "groups": enriched,
        "ranking_for": ranking_for,
        "ranking_against": ranking_against,
        "max_for": max_for,
        "min_for": min_for,
        "delta_for": max_for["FOR"] - min_for["FOR"],
    }


def compute_political_signals(metrics: dict) -> dict:
    """Derive dataset-level political signals from precomputed vote metrics.

    All computation is pure Python and fully deterministic.

    Signals:
        consensus_score    (float)  Percentage of groups sharing the same
                                    dominant vote category. Range: 0–100.
        polarization_score (float)  Population standard deviation of FOR values
                                    across groups. 0.0 when only one group.
        abstention_signal  (int)    Count of groups where ABSTAIN strictly
                                    exceeds both FOR and AGAINST.
        dominant_bloc      (str)    "FOR" | "AGAINST" | "TIED" — whichever
                                    category has the higher total across all groups.

    Args:
        metrics: Output of compute_vote_metrics().

    Returns:
        Dict with keys: consensus_score, polarization_score,
        abstention_signal, dominant_bloc.
    """
    groups = metrics["groups"]

    if not groups:
        return {
            "consensus_score": 0.0,
            "polarization_score": 0.0,
            "abstention_signal": 0,
            "dominant_bloc": "N/A",
        }

    # consensus_score — share of groups whose dominant category is the same.
    # Ties inside a group are broken by category order: FOR > AGAINST > ABSTAIN.
    dominant_per_group = [
        max(_VOTE_LABELS, key=lambda v: g[v])
        for g in groups
    ]
    most_common_count = Counter(dominant_per_group).most_common(1)[0][1]
    consensus_score = round(most_common_count / len(groups) * 100, 1)

    # polarization_score — population std dev of FOR counts across groups.
    for_values = [g["FOR"] for g in groups]
    polarization_score = round(statistics.pstdev(for_values), 4)

    # abstention_signal — groups where ABSTAIN is strictly the highest value.
    abstention_signal = sum(
        1 for g in groups
        if g["ABSTAIN"] > g["FOR"] and g["ABSTAIN"] > g["AGAINST"]
    )

    # dominant_bloc — aggregate FOR vs AGAINST totals across all groups.
    total_for = sum(g["FOR"] for g in groups)
    total_against = sum(g["AGAINST"] for g in groups)
    if total_for > total_against:
        dominant_bloc = "FOR"
    elif total_against > total_for:
        dominant_bloc = "AGAINST"
    else:
        dominant_bloc = "TIED"

    return {
        "consensus_score": consensus_score,
        "polarization_score": polarization_score,
        "abstention_signal": abstention_signal,
        "dominant_bloc": dominant_bloc,
    }


def generate_ai_insight(summary_dict: VoteSummary, topic: str, lang: str = "English") -> str:
    """Return a data-driven AI summary of voting patterns via Groq (free tier).

    Requires GROQ_API_KEY in .env — get a free key at console.groq.com.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key or api_key == "your_groq_api_key_here":
        return "NO_KEY"

    summary_list = [
        {"group": group, "FOR": counts["FOR"], "AGAINST": counts["AGAINST"], "ABSTAIN": counts["ABSTAIN"]}
        for group, counts in summary_dict.items()
    ]
    metrics = compute_vote_metrics(summary_list)

    # Determine outcome from dominant bloc
    dominant = "PASSED" if metrics["groups"] and sum(g["FOR"] for g in metrics["groups"]) > sum(g["AGAINST"] for g in metrics["groups"]) else "REJECTED"

    # Left/right orientation per group (simplified)
    left_groups  = {"S&D", "Greens/EFA", "The Left"}
    right_groups = {"EPP", "ECR", "Patriots for Europe", "ESN", "ID"}
    center_groups = {"Renew"}

    group_summary = []
    for g in metrics["groups"]:
        name = g["group"]
        dominant_vote = "FOR" if g["FOR"] >= g["AGAINST"] else "AGAINST"
        if name in left_groups:
            side = "left-wing"
        elif name in right_groups:
            side = "right-wing"
        elif name in center_groups:
            side = "centrist"
        else:
            side = "other"
        group_summary.append(f"- {name} ({side}): {dominant_vote} ({g['FOR']} for / {g['AGAINST']} against)")

    group_text = "\n".join(group_summary)

    prompt = f"""You are explaining an EU Parliament vote to someone with no political knowledge. Be clear, simple, and neutral.

VOTE TOPIC: {topic}

RESULT: The vote {dominant}.

HOW EACH GROUP VOTED:
{group_text}

Write a short explanation (4-6 sentences) that covers:
1. In plain language, what this vote was about (explain the topic as if to a curious teenager)
2. Which political side (left/right/center) supported or opposed it, and why that makes sense
3. Whether it passed or failed, and what that means in practice

Use simple language. No jargon. No bullet points — write in flowing sentences.

Respond entirely in {lang}."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.1,
            },
            timeout=15,
        )
        if response.status_code == 200:
            return validate_output(response.json()["choices"][0]["message"]["content"])
        elif response.status_code == 401:
            return "BAD_KEY"
        elif response.status_code == 429:
            return "RATE_LIMIT"
        elif response.status_code == 404:
            logger.warning("Groq 404 — model not found: %s", response.text[:200])
            return "API_ERROR"
        else:
            logger.warning("Groq returned %s: %s", response.status_code, response.text[:300])
            return "API_ERROR"
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as exc:
        logger.warning("Groq request failed: %s", exc)
        return "API_ERROR"

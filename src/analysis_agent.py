import logging
import statistics
from collections import Counter

import requests
import pandas as pd

from config import settings

# vote counts per political group, e.g. {"EPP": {"FOR": 2, "AGAINST": 1, "ABSTAIN": 0}}
VoteSummary = dict[str, dict[str, int]]

logger = logging.getLogger(__name__)

_VOTE_LABELS = ["FOR", "AGAINST", "ABSTAIN"]


def build_summary(votes_df: pd.DataFrame) -> VoteSummary:
    """Groups votes by political group and counts FOR/AGAINST/ABSTAIN for each."""
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
    """Filters the dataset to a specific topic and returns the vote breakdown."""
    filtered = votes_df[votes_df["policy_topic"] == topic]
    if filtered.empty:
        raise ValueError(
            f"No voting records found for topic '{topic}'. "
            f"Available topics: {sorted(votes_df['policy_topic'].unique().tolist())}"
        )
    return build_summary(filtered)


def validate_output(text: str) -> str:
    """Rejects obviously broken LLM responses."""
    if not text or len(text.strip()) < 20:
        return "API_ERROR"
    return text


def compute_vote_metrics(summary_list: list[dict]) -> dict:
    """Calculates totals, ratios and rankings from the raw vote counts."""
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
    """Derives consensus, polarization and abstention signals from vote metrics."""
    groups = metrics["groups"]

    if not groups:
        return {
            "consensus_score": 0.0,
            "polarization_score": 0.0,
            "abstention_signal": 0,
            "dominant_bloc": "N/A",
        }

    # what fraction of groups share the same dominant vote
    dominant_per_group = [
        max(_VOTE_LABELS, key=lambda v: g[v])
        for g in groups
    ]
    most_common_count = Counter(dominant_per_group).most_common(1)[0][1]
    consensus_score = round(most_common_count / len(groups) * 100, 1)

    # spread of FOR votes across groups
    for_values = [g["FOR"] for g in groups]
    polarization_score = round(statistics.pstdev(for_values), 4)

    # how many groups abstained more than they voted either way
    abstention_signal = sum(
        1 for g in groups
        if g["ABSTAIN"] > g["FOR"] and g["ABSTAIN"] > g["AGAINST"]
    )

    # overall winner
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
    """Calls Groq to generate a short neutral summary of a vote. Needs GROQ_API_KEY."""
    api_key = settings.GROQ_API_KEY
    if not api_key or api_key == "your_groq_api_key_here":
        return "NO_KEY"

    summary_list = [
        {"group": group, "FOR": counts["FOR"], "AGAINST": counts["AGAINST"], "ABSTAIN": counts["ABSTAIN"]}
        for group, counts in summary_dict.items()
    ]
    metrics = compute_vote_metrics(summary_list)

    dominant = "PASSED" if metrics["groups"] and sum(g["FOR"] for g in metrics["groups"]) > sum(g["AGAINST"] for g in metrics["groups"]) else "REJECTED"

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

    prompt = f"""IMPORTANT: You MUST write your entire response in {lang}. Every single sentence must be in {lang}. Do not use English if {lang} is not English.

You are a strictly neutral political reporter explaining an EU Parliament vote in plain language. You have no political opinion. You never express approval, disapproval, hope, or disappointment about any outcome.

VOTE TOPIC: {topic}

RESULT: The vote {dominant}.

HOW EACH GROUP VOTED:
{group_text}

Write a short explanation (4-6 sentences) covering:
1. What this vote was about, explained in plain language (as if to someone with no political background)
2. Which political groups voted for and against, stated as pure facts
3. What the outcome means in practice — factually, with zero judgment

STRICT RULES — never break these:
- Never use words like "fortunately", "unfortunately", "sadly", "good news", "bad news", "worryingly", "thankfully", or any word that implies an opinion on the outcome.
- Never say one side was "right" or "wrong", "wise" or "unwise".
- Describe what happened. Do not editorialize.
- Write in flowing sentences, no bullet points, no jargon.

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
                "messages": [
                    {"role": "system", "content": f"You are a neutral political analyst. You MUST respond entirely in {lang}. Never use English if the requested language is not English."},
                    {"role": "user", "content": prompt},
                ],
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
    except Exception as e:
        logger.error("AI insight error: %s", e)
        return "API_ERROR"

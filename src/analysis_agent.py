import logging
import statistics
from collections import Counter

import anthropic
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
    """Reject LLM responses that contain hallucinated political reasoning."""
    forbidden = [
        "alliance", "aligned", "coalition",
        "ideology", "unexpected", "supports same",
    ]
    for word in forbidden:
        if word in text.lower():
            logger.warning("Hallucination detected — forbidden word %r in LLM output.", word)
            return "Error: invalid AI output (hallucination detected)"
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


def _ollama_insight(prompt: str) -> str:
    """Fallback: call Ollama locally at port 11434."""
    import requests
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        if response.status_code == 200:
            result = response.json()["response"]
            return validate_output(result)
        else:
            raise Exception(f"Ollama returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama not running — start it with: ollama serve")


def generate_ai_insight(summary_dict: VoteSummary, topic: str) -> str:
    """Return a strictly data-driven statistical summary of voting patterns.

    Converts the VoteSummary dict to a structured list before passing to the
    LLM so the model receives explicit, enumerated rows rather than a raw dict.
    The response is validated against a forbidden-word list before being returned.

    Args:
        summary_dict: Aggregated vote counts from :func:`build_summary` or
            :func:`analyze_policy`.
        topic:        Policy topic label used to contextualise the prompt.

    Returns:
        Validated LLM response string, or an error string prefixed with "Error:".
    """
    # Convert to flat list, then compute all metrics in Python — not the LLM.
    summary_list = [
        {"group": group, "FOR": counts["FOR"], "AGAINST": counts["AGAINST"], "ABSTAIN": counts["ABSTAIN"]}
        for group, counts in summary_dict.items()
    ]
    metrics = compute_vote_metrics(summary_list)

    prompt = f"""[INST]
YOU ARE A TEXT FORMATTER ONLY.
DO NOT COMPUTE ANYTHING.
USE ONLY THE VALUES PROVIDED BELOW — COPY THEM VERBATIM.

TOPIC: {topic}

PRECOMPUTED VALUES (do not recalculate):
- Groups: {metrics["groups"]}
- Ranking by FOR (high→low): {metrics["ranking_for"]}
- Ranking by AGAINST (high→low): {metrics["ranking_against"]}
- Highest FOR: {metrics["max_for"]}
- Lowest FOR: {metrics["min_for"]}
- Delta FOR: {metrics["delta_for"]}

OUTPUT FORMAT (copy values only, no additions, no interpretation):

BLOCS:
- <group>: FOR=<n> AGAINST=<n> ABSTAIN=<n>
(one line per group, values from Groups list)

RANKING_FOR:
- <group> (<n>), ... (from Ranking by FOR)

RANKING_AGAINST:
- <group> (<n>), ... (from Ranking by AGAINST)

HIGHEST_FOR:
- <group> with FOR=<n> (from Highest FOR)

LOWEST_FOR:
- <group> with FOR=<n> (from Lowest FOR)

DELTA_FOR:
- <n> (from Delta FOR, copy only)

CLEAVAGE:
- max(FOR)=<n>, min(FOR)=<n>, delta=<n>

EXECUTIVE_SUMMARY:
• Total groups: <n>
• Group with most FOR votes: <group> (<n>)
• FOR vote spread (delta): <n>

COPY VALUES ONLY. NO CALCULATIONS. NO INTERPRETATION.
[/INST]"""

    if not settings.ANTHROPIC_API_KEY:
        logger.info("No ANTHROPIC_API_KEY — using Ollama fallback.")
        try:
            return _ollama_insight(prompt)
        except Exception:
            return "⚠️ Start Ollama to enable AI insights: run 'ollama serve' in a terminal"

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
        logger.debug("Raw Claude output for topic %r: %s", topic, raw)
        return validate_output(raw)
    except anthropic.AuthenticationError:
        return "Error: Anthropic API key is missing or invalid. Set ANTHROPIC_API_KEY in your .env file."
    except anthropic.RateLimitError:
        return "Error: Anthropic rate limit reached. Try again in a few seconds."
    except Exception as exc:
        logger.exception("Claude API call failed for topic %r", topic)
        return f"Error: Claude API call failed — {exc}"

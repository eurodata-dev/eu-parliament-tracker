import pandas as pd

VOTE_LABELS = ["FOR", "AGAINST", "ABSTAIN"]


def _vote_shares(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Calculates % FOR / AGAINST / ABSTAIN for each value in group_col."""
    if df.empty or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, "pct_FOR", "pct_AGAINST", "pct_ABSTAIN"])

    counts = (
        df.groupby([group_col, "vote"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=VOTE_LABELS, fill_value=0)
    )
    totals = counts.sum(axis=1).replace(0, pd.NA)
    shares = (counts.div(totals, axis=0) * 100).round(2)
    shares.columns = [f"pct_{v}" for v in VOTE_LABELS]
    return shares.reset_index()


def compute_group_behavior(df: pd.DataFrame) -> pd.DataFrame:
    """Vote share breakdown per political group."""
    return _vote_shares(df, "political_group")


def compute_topic_behavior(df: pd.DataFrame) -> pd.DataFrame:
    """Vote share breakdown per policy topic."""
    return _vote_shares(df, "policy_topic")


def _drift_table(hist: pd.DataFrame, recent: pd.DataFrame, key_col: str) -> dict:
    """Computes how much each group/topic shifted between historical and recent data."""
    hist_indexed = hist.set_index(key_col) if not hist.empty else pd.DataFrame()
    recent_indexed = recent.set_index(key_col) if not recent.empty else pd.DataFrame()

    all_keys = set(hist_indexed.index) | set(recent_indexed.index)
    share_cols = ["pct_FOR", "pct_AGAINST", "pct_ABSTAIN"]

    result = {}
    for key in sorted(all_keys):
        hist_row = hist_indexed.loc[key, share_cols] if key in hist_indexed.index else pd.Series([0.0] * 3, index=share_cols)
        recent_row = recent_indexed.loc[key, share_cols] if key in recent_indexed.index else pd.Series([0.0] * 3, index=share_cols)

        delta = (recent_row - hist_row).round(2)
        result[key] = {
            "delta_FOR": delta["pct_FOR"],
            "delta_AGAINST": delta["pct_AGAINST"],
            "delta_ABSTAIN": delta["pct_ABSTAIN"],
        }

    return result


def _top_changers(drift: dict, n: int = 5) -> list[str]:
    """Returns the top N groups/topics that changed the most."""
    scored = {
        key: abs(v["delta_FOR"]) + abs(v["delta_AGAINST"]) + abs(v["delta_ABSTAIN"])
        for key, v in drift.items()
    }
    return sorted(scored, key=scored.get, reverse=True)[:n]


def _polarization(df: pd.DataFrame) -> float:
    """Simple polarization metric based on how far FOR% is from 50."""
    if df.empty or "pct_FOR" not in df.columns:
        return 0.0
    return round(float((df["pct_FOR"] - 50.0).abs().mean()), 2)


def compare_behavior(historical_df: pd.DataFrame, recent_df: pd.DataFrame) -> dict:
    """Compares historical and recent voting patterns to find what changed."""
    hist_groups = compute_group_behavior(historical_df)
    recent_groups = compute_group_behavior(recent_df)
    hist_topics = compute_topic_behavior(historical_df)
    recent_topics = compute_topic_behavior(recent_df)

    group_drift = _drift_table(hist_groups, recent_groups, "political_group")
    topic_drift = _drift_table(hist_topics, recent_topics, "policy_topic")

    top_groups = _top_changers(group_drift)
    top_topics = _top_changers(topic_drift)

    pol_hist = _polarization(hist_groups)
    pol_recent = _polarization(recent_groups)
    polarization_change = round(pol_recent - pol_hist, 2)

    summary = {
        "most_changed_group": top_groups[0] if top_groups else None,
        "most_changed_topic": top_topics[0] if top_topics else None,
        "overall_polarization_change": polarization_change,
        "top_5_changed_groups": top_groups,
        "top_5_changed_topics": top_topics,
    }

    return {
        "group_drift": group_drift,
        "topic_drift": topic_drift,
        "summary": summary,
    }

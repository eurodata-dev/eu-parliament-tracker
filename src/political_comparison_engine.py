import pandas as pd

VOTE_LABELS = ["FOR", "AGAINST", "ABSTAIN"]


def _vote_shares(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Return % FOR / AGAINST / ABSTAIN per value of group_col."""
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
    """Return per-political-group vote share (% FOR / AGAINST / ABSTAIN).

    Args:
        df: DataFrame with columns member_name, political_group, policy_topic,
            vote, date.

    Returns:
        DataFrame indexed by political_group with columns
        pct_FOR, pct_AGAINST, pct_ABSTAIN.
    """
    return _vote_shares(df, "political_group")


def compute_topic_behavior(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-policy-topic vote share (% FOR / AGAINST / ABSTAIN).

    Args:
        df: DataFrame with columns member_name, political_group, policy_topic,
            vote, date.

    Returns:
        DataFrame indexed by policy_topic with columns
        pct_FOR, pct_AGAINST, pct_ABSTAIN.
    """
    return _vote_shares(df, "policy_topic")


def _drift_table(hist: pd.DataFrame, recent: pd.DataFrame, key_col: str) -> dict:
    """Compute per-key delta (recent − historical) for all three vote shares."""
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
    """Return the top-N keys by absolute total drift across all vote types."""
    scored = {
        key: abs(v["delta_FOR"]) + abs(v["delta_AGAINST"]) + abs(v["delta_ABSTAIN"])
        for key, v in drift.items()
    }
    return sorted(scored, key=scored.get, reverse=True)[:n]


def _polarization(df: pd.DataFrame) -> float:
    """Measure polarization as the average absolute deviation of FOR% from 50."""
    if df.empty or "pct_FOR" not in df.columns:
        return 0.0
    return round(float((df["pct_FOR"] - 50.0).abs().mean()), 2)


def compare_behavior(historical_df: pd.DataFrame, recent_df: pd.DataFrame) -> dict:
    """Compare historical vs recent voting behavior and surface changes.

    Args:
        historical_df: Full historical votes DataFrame.
        recent_df:     Recent-window votes DataFrame (same schema).

    Returns:
        {
            "group_drift": {
                "<group>": {"delta_FOR": float, "delta_AGAINST": float, "delta_ABSTAIN": float},
                ...
            },
            "topic_drift": {
                "<topic>": {"delta_FOR": float, "delta_AGAINST": float, "delta_ABSTAIN": float},
                ...
            },
            "summary": {
                "most_changed_group": str | None,
                "most_changed_topic": str | None,
                "overall_polarization_change": float,
                "top_5_changed_groups": list[str],
                "top_5_changed_topics": list[str],
            },
        }
    """
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

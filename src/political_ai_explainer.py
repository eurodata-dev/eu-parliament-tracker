def explain_political_changes(comparison_results: dict, topic: str = None) -> str:
    """Convert structured comparison results into a journalist-friendly summary.

    Args:
        comparison_results: Output dict from political_comparison_engine.compare_behavior().
        topic: Optional policy topic to focus the explanation on.

    Returns:
        A plain-English summary string (5–10 sentences).
    """
    summary = comparison_results.get("summary", {})
    group_drift = comparison_results.get("group_drift", {})
    topic_drift = comparison_results.get("topic_drift", {})

    if not summary and not group_drift and not topic_drift:
        return "No comparison data is available to explain."

    sentences = []

    # --- Opening framing ---
    if topic:
        matched = {t: v for t, v in topic_drift.items() if topic.lower() in t.lower()}
        if matched:
            sentences.append(
                f"The following observations focus on recent voting shifts related to '{topic}'."
            )
        else:
            return f"No data found for topic '{topic}' in the comparison results."
    else:
        sentences.append(
            "Here is an overview of how voting behavior has shifted between the historical and recent periods."
        )

    # --- Most changed group ---
    most_changed_group = summary.get("most_changed_group")
    if most_changed_group and most_changed_group in group_drift:
        g = group_drift[most_changed_group]
        direction = _dominant_direction(g)
        sentences.append(
            f"The political group that changed its voting behavior the most is {most_changed_group}, "
            f"which moved notably {direction}."
        )

    # --- Top 5 groups ---
    top_groups = summary.get("top_5_changed_groups", [])
    if len(top_groups) > 1:
        others = ", ".join(top_groups[1:4])
        sentences.append(
            f"Other groups showing significant shifts include {others}."
        )

    # --- Topic focus or most changed topic ---
    if topic and matched:
        for topic_name, drift in matched.items():
            direction = _dominant_direction(drift)
            sentences.append(
                f"On '{topic_name}', recent votes have shifted {direction} "
                f"(FOR: {_fmt(drift['delta_FOR'])}, AGAINST: {_fmt(drift['delta_AGAINST'])}, "
                f"ABSTAIN: {_fmt(drift['delta_ABSTAIN'])})."
            )
    else:
        most_changed_topic = summary.get("most_changed_topic")
        if most_changed_topic and most_changed_topic in topic_drift:
            t = topic_drift[most_changed_topic]
            direction = _dominant_direction(t)
            sentences.append(
                f"The policy topic with the largest voting shift is '{most_changed_topic}', "
                f"where support has moved {direction}."
            )

        top_topics = summary.get("top_5_changed_topics", [])
        if len(top_topics) > 1:
            other_topics = ", ".join(f"'{t}'" for t in top_topics[1:4])
            sentences.append(
                f"Notable shifts also appear in {other_topics}."
            )

    # --- Polarization ---
    pol_change = summary.get("overall_polarization_change")
    if pol_change is not None:
        if abs(pol_change) < 1.0:
            sentences.append(
                "Overall, the level of political polarization has remained relatively stable."
            )
        elif pol_change > 0:
            sentences.append(
                f"Overall polarization has increased by {pol_change:.1f} percentage points, "
                "suggesting groups are diverging more than before."
            )
        else:
            sentences.append(
                f"Overall polarization has decreased by {abs(pol_change):.1f} percentage points, "
                "suggesting some convergence across groups."
            )

    # --- Closing ---
    if not topic:
        sentences.append(
            "These changes reflect observable differences in recorded vote counts "
            "and do not imply conclusions about political intent."
        )

    return " ".join(sentences)


def _dominant_direction(drift: dict) -> str:
    """Return the label of the largest absolute change in a drift entry."""
    mapping = {
        "FOR": drift.get("delta_FOR", 0.0),
        "AGAINST": drift.get("delta_AGAINST", 0.0),
        "ABSTAIN": drift.get("delta_ABSTAIN", 0.0),
    }
    label = max(mapping, key=lambda k: abs(mapping[k]))
    value = mapping[label]
    qualifier = "more" if value >= 0 else "less"
    return f"{qualifier} toward {label} votes"


def _fmt(value: float) -> str:
    """Format a delta value with a sign prefix."""
    return f"{value:+.1f}%"

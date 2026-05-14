import os
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from eu_api import fetch_all_votes
from analysis_agent import analyze_policy, generate_ai_insight
from eu_dataset_loader import get_eu_votes
from recent_data_loader import load_recent_votes
from political_comparison_engine import compare_behavior, compute_group_behavior
from political_ai_explainer import explain_political_changes

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="EU Parliament Vote Tracker",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Default buttons → pill style (suggestions) */
    .stButton > button {
        border-radius: 20px;
        font-size: 0.82rem;
        padding: 0.25rem 0.85rem;
        background-color: #f3f4f6;
        color: #374151;
        border: 1px solid #e5e7eb;
        transition: all 0.15s;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stButton > button:hover {
        background-color: #dbeafe;
        border-color: #3b82f6;
        color: #1d4ed8;
    }
    /* Primary buttons keep standard look */
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 0.5rem 2rem !important;
    }
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 6px;
    }
    /* Topic context bar */
    .topic-bar {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 12px 20px;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    /* Verdict badges */
    .verdict-passed   { background:#dcfce7; color:#166534; padding:5px 16px; border-radius:20px; font-weight:600; font-size:0.95rem; display:inline-block; margin-top:0.8rem; }
    .verdict-rejected { background:#fee2e2; color:#991b1b; padding:5px 16px; border-radius:20px; font-weight:600; font-size:0.95rem; display:inline-block; margin-top:0.8rem; }
    .verdict-contested{ background:#fef9c3; color:#854d0e; padding:5px 16px; border-radius:20px; font-weight:600; font-size:0.95rem; display:inline-block; margin-top:0.8rem; }
    /* Big metric cards */
    .result-card { text-align:center; padding:1.2rem 1rem; border-radius:10px; }
    .result-card .icon { font-size:2rem; }
    .result-card .pct  { font-size:2.6rem; font-weight:800; line-height:1.1; }
    .result-card .label{ font-size:0.9rem; color:#6b7280; margin-top:0.2rem; }
    /* AI analysis card */
    .ai-card { background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:1.2rem 1.5rem; margin-top:0.5rem; white-space:pre-wrap; font-size:0.92rem; }
    /* Search hint */
    .search-hint { text-align:center; color:#9ca3af; font-size:0.82rem; margin-top:0.3rem; }
</style>
""", unsafe_allow_html=True)

# ── Runtime flags ─────────────────────────────────────────────────────────────

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")
_DEMO_ROW_LIMIT = 5000
_DATA_DIR = Path(__file__).parent.parent / "data"

# ── Synonym expansion ─────────────────────────────────────────────────────────

_SYNONYMS: dict[str, list[str]] = {
    "AI":   ["artificial intelligence", "intelligence artificielle"],
    "EP":   ["european parliament"],
    "DSA":  ["digital services"],
    "GDPR": ["data protection"],
}

# ── Cached data loaders ───────────────────────────────────────────────────────


@st.cache_data
def get_votes() -> pd.DataFrame:
    return fetch_all_votes()


@st.cache_data
def get_historical_votes() -> pd.DataFrame:
    df = get_eu_votes()
    if DEMO_MODE and len(df) > _DEMO_ROW_LIMIT:
        df = df.tail(_DEMO_ROW_LIMIT).reset_index(drop=True)
    return df


@st.cache_data
def get_recent_votes(days: int = 30) -> pd.DataFrame:
    return load_recent_votes(days)


@st.cache_data
def get_cached_comparison(
    historical_df: pd.DataFrame, recent_df: pd.DataFrame
) -> dict:
    return compare_behavior(historical_df, recent_df)


# ── Search helpers ────────────────────────────────────────────────────────────


def _search_df(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Filter df rows whose policy_topic matches query with word-boundary rules."""
    q = query.strip()
    if len(q) <= 1:
        return df.iloc[:0]
    if len(q) == 2:
        if q != q.upper():
            return df.iloc[:0]  # 2-char must be ALL UPPERCASE (abbreviations)
        pattern = r'\b' + re.escape(q) + r'\b'
        mask = df["policy_topic"].str.contains(pattern, case=True, na=False, regex=True)
    else:
        pattern = r'\b' + re.escape(q) + r'\b'
        mask = df["policy_topic"].str.contains(pattern, case=False, na=False, regex=True)

    for syn in _SYNONYMS.get(q.upper(), []):
        syn_pat = r'\b' + re.escape(syn) + r'\b'
        mask = mask | df["policy_topic"].str.contains(syn_pat, case=False, na=False, regex=True)

    return df[mask]


def _get_suggestions(df: pd.DataFrame, query: str) -> list[tuple[str, int]]:
    """Return (topic, vote_count) pairs sorted: starts-with first, then by count desc."""
    matched = _search_df(df, query)
    if matched.empty:
        return []

    counts = (
        matched.groupby("policy_topic")
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
    )

    q_lower = query.lower()
    starts = counts[counts["policy_topic"].str.lower().str.startswith(q_lower)]
    others = counts[~counts["policy_topic"].str.lower().str.startswith(q_lower)]
    ranked = pd.concat([starts, others]).head(15)

    return [(row["policy_topic"], int(row["n"])) for _, row in ranked.iterrows()]


# ── Load primary dataset ──────────────────────────────────────────────────────

votes_df = get_votes()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🇪🇺 EU Parliament")
    st.caption("Vote Tracker")
    st.divider()

    parquet_exists  = (_DATA_DIR / "processed" / "eu_votes_real.parquet").exists()
    real_csv_exists = (_DATA_DIR / "processed" / "eu_votes_real.csv").exists()
    sample_exists   = (_DATA_DIR / "raw" / "eu_votes_sample.csv").exists()
    live_files      = list((_DATA_DIR / "recent").glob("*.csv")) if (_DATA_DIR / "recent").exists() else []

    if parquet_exists:
        st.success(f"📦 {len(votes_df):,} votes loaded")
    elif real_csv_exists:
        st.info(f"📄 {len(votes_df):,} votes (CSV)")
    elif sample_exists:
        st.warning(f"🔬 Sample — {len(votes_df):,} votes")
    else:
        st.warning(f"⚡ {len(votes_df):,} votes (fallback)")

    if live_files:
        st.success("🟢 Live data included")

    st.divider()
    st.subheader("Filters")

    valid_dates = votes_df["date"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    else:
        date_range = None

    all_groups = sorted(votes_df["political_group"].dropna().unique().tolist())
    _g1, _g2 = st.columns(2)
    if _g1.button("Select all", use_container_width=True):
        st.session_state["group_filter"] = all_groups
        st.rerun()
    if _g2.button("Clear all", use_container_width=True):
        st.session_state["group_filter"] = []
        st.rerun()
    selected_groups = st.multiselect(
        "Political groups",
        options=all_groups,
        default=all_groups,
        key="group_filter",
        label_visibility="collapsed",
    )
    if not selected_groups:
        st.warning("Select at least one group.")

    st.divider()

    if st.button(
        "🔄 Refresh live data",
        use_container_width=True,
        help="Fetches the latest votes from the EU Parliament API and adds them to the dataset",
    ):
        with st.spinner("Fetching latest EP votes…"):
            try:
                import ep_live_fetcher
                ep_live_fetcher.run()
                st.cache_data.clear()
                st.success("Live data refreshed!")
                st.rerun()
            except Exception as exc:
                st.error(f"Fetch failed: {exc}")

# ── Apply sidebar filters ─────────────────────────────────────────────────────

filtered_df = votes_df.copy()

if date_range and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["date"] >= pd.Timestamp(start_date)) &
        (filtered_df["date"] <= pd.Timestamp(end_date))
    ]

if selected_groups:
    filtered_df = filtered_df[filtered_df["political_group"].isin(selected_groups)]

available_topics = sorted(filtered_df["policy_topic"].dropna().unique().tolist())

# ── Search state management ───────────────────────────────────────────────────

if "search_override" in st.session_state:
    default_val = st.session_state.pop("search_override")
    st.session_state.pop("main_search", None)
else:
    default_val = st.session_state.get("main_search", "")

# ── HEADER ────────────────────────────────────────────────────────────────────

st.title("EU Parliament Vote Tracker")
st.markdown(
    f"<p style='color:#6b7280;font-size:1.05rem;margin-top:-0.5rem;'>"
    f"Search {len(votes_df):,} votes from the European Parliament (2019–2026)</p>",
    unsafe_allow_html=True,
)

if DEMO_MODE:
    st.info(
        "**Demo Mode** — dataset capped at 5,000 rows. "
        "Set `DEMO_MODE=false` to enable full analysis."
    )

# ── SEARCH ────────────────────────────────────────────────────────────────────

_, search_col, _ = st.columns([1, 4, 1])

with search_col:
    query = st.text_input(
        "Search",
        value=default_val,
        key="main_search",
        placeholder="Search any topic — e.g. AI, Ukraine, climate, pharma...",
        label_visibility="collapsed",
    )
    st.markdown(
        '<p class="search-hint">'
        "Type a topic to see matching votes · 2-letter uppercase for abbreviations (AI, EP…)"
        "</p>",
        unsafe_allow_html=True,
    )

    suggestions = _get_suggestions(filtered_df, query) if query else []

    if suggestions:
        for row_start in range(0, len(suggestions), 3):
            row = suggestions[row_start : row_start + 3]
            pill_cols = st.columns(len(row))
            for i, (topic_name, vote_n) in enumerate(row):
                display = (topic_name[:50] + "…" if len(topic_name) > 50 else topic_name)
                label = f"{display} · {vote_n:,}"
                if pill_cols[i].button(label, key=f"pill_{row_start}_{i}", use_container_width=True):
                    st.session_state["search_override"] = topic_name
                    st.rerun()
    elif query and (len(query) >= 3 or (len(query) == 2 and query == query.upper())):
        st.markdown(
            '<p style="color:#9ca3af;font-size:0.85rem;text-align:center;">No matching topics found.</p>',
            unsafe_allow_html=True,
        )

# ── RESOLVE SELECTED TOPIC ────────────────────────────────────────────────────

topic = None

if query:
    exact = filtered_df[filtered_df["policy_topic"] == query]["policy_topic"].unique().tolist()
    if exact:
        topic = exact[0]
    else:
        unique_matches = (
            _search_df(filtered_df, query)["policy_topic"]
            .dropna()
            .unique()
            .tolist()
        )
        if len(unique_matches) == 1:
            topic = unique_matches[0]
        elif len(unique_matches) > 1:
            topic = st.selectbox("Multiple topics match — select one:", unique_matches)

# ── RESULTS ───────────────────────────────────────────────────────────────────

if topic:
    topic_df = filtered_df[filtered_df["policy_topic"] == topic]

    # Context bar
    t_dates = topic_df["date"].dropna()
    if not t_dates.empty:
        d_range_str = f"{t_dates.min().strftime('%b %Y')} – {t_dates.max().strftime('%b %Y')}"
    else:
        d_range_str = "—"

    st.markdown(
        f'<div class="topic-bar">'
        f'<strong>{topic}</strong><br>'
        f'<span style="color:#6b7280;font-size:0.9rem;">'
        f'{len(topic_df):,} votes &nbsp;·&nbsp; {d_range_str}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    # ── Section 1: How did parties vote? ──────────────────────────────────────

    st.subheader("How did parties vote?")

    group_votes = (
        topic_df.groupby(["political_group", "vote"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["FOR", "AGAINST", "ABSTAIN"], fill_value=0)
    )

    if not group_votes.empty:
        group_votes["Total"] = group_votes.sum(axis=1)
        for col in ("FOR", "AGAINST", "ABSTAIN"):
            group_votes[f"{col}_%"] = (
                group_votes[col] / group_votes["Total"].replace(0, 1) * 100
            ).round(1)

        plot_df = (
            group_votes
            .sort_values("FOR_%", ascending=True)  # ascending → highest FOR at top of chart
            .reset_index()
        )

        fig = px.bar(
            plot_df,
            y="political_group",
            x=["FOR_%", "AGAINST_%", "ABSTAIN_%"],
            orientation="h",
            barmode="stack",
            color_discrete_map={
                "FOR_%":     "#2563eb",
                "AGAINST_%": "#ef4444",
                "ABSTAIN_%": "#d1d5db",
            },
            title="Vote breakdown by political group",
        )
        for trace in fig.data:
            trace.name = {"FOR_%": "FOR", "AGAINST_%": "AGAINST", "ABSTAIN_%": "ABSTAIN"}.get(
                trace.name, trace.name
            )
            trace.hovertemplate = "%{y}: %{x:.1f}%<extra>" + trace.name + "</extra>"
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
            legend_title_text="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=20, t=55, b=10),
            height=max(300, len(plot_df) * 40 + 90),
            title_font_size=14,
        )
        fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=True, gridcolor="#f3f4f6", zeroline=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No voting data for this topic.")

    st.divider()

    # ── Section 2: Overall result ──────────────────────────────────────────────

    st.subheader("Overall result")

    vote_counts = topic_df["vote"].value_counts()
    total_v     = len(topic_df)
    for_n       = int(vote_counts.get("FOR", 0))
    against_n   = int(vote_counts.get("AGAINST", 0))
    abstain_n   = int(vote_counts.get("ABSTAIN", 0))
    for_pct     = round(for_n     / total_v * 100, 1) if total_v else 0.0
    against_pct = round(against_n / total_v * 100, 1) if total_v else 0.0
    abstain_pct = round(abstain_n / total_v * 100, 1) if total_v else 0.0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<div class="result-card" style="background:#eff6ff;">'
            f'<div class="icon">✅</div>'
            f'<div class="pct" style="color:#2563eb;">{for_pct:.1f}%</div>'
            f'<div class="label">FOR — {for_n:,} votes</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="result-card" style="background:#fff1f2;">'
            f'<div class="icon">❌</div>'
            f'<div class="pct" style="color:#ef4444;">{against_pct:.1f}%</div>'
            f'<div class="label">AGAINST — {against_n:,} votes</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="result-card" style="background:#f9fafb;">'
            f'<div class="icon">○</div>'
            f'<div class="pct" style="color:#6b7280;">{abstain_pct:.1f}%</div>'
            f'<div class="label">ABSTAIN — {abstain_n:,} votes</div></div>',
            unsafe_allow_html=True,
        )

    if for_pct > 55:
        verdict_html = '<span class="verdict-passed">Motion passed</span>'
    elif for_pct >= 45:
        verdict_html = '<span class="verdict-contested">Contested — close result</span>'
    else:
        verdict_html = '<span class="verdict-rejected">Motion rejected</span>'

    st.markdown(
        f'<div style="margin-top:1rem;">{verdict_html}</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Section 3: AI Analysis ─────────────────────────────────────────────────

    st.subheader("AI Analysis")

    if DEMO_MODE:
        st.info("AI Analysis is disabled in Demo Mode. Set `DEMO_MODE=false` to enable.")
    else:
        if st.button("Generate AI Analysis", type="primary"):
            try:
                topic_summary = analyze_policy(filtered_df, topic)
            except ValueError as exc:
                st.error(str(exc))
                st.stop()

            with st.spinner("Analyzing voting patterns…"):
                insight = generate_ai_insight(topic_summary, topic)

            if "Start Ollama" in insight or insight.startswith("⚠️"):
                st.warning("💡 Start Ollama to enable AI analysis: run `ollama serve`")
            elif insight.startswith("Error:"):
                st.warning(insight)
            else:
                st.markdown(
                    f'<div class="ai-card">{insight}</div>',
                    unsafe_allow_html=True,
                )

    st.divider()

# ── Recent Political Changes (conditional) ────────────────────────────────────

recent_dir = _DATA_DIR / "recent"
has_recent_data = False
if recent_dir.exists():
    for csv_file in recent_dir.glob("*.csv"):
        try:
            _tmp = pd.read_csv(csv_file)
            if len(_tmp) > 0:
                has_recent_data = True
                break
        except Exception:
            pass

if has_recent_data:
    st.header("Recent Political Changes")
    st.caption("Compares voting behavior from the last 30 days against the full historical dataset.")

    historical_df = get_historical_votes()

    st.subheader("Historical Insight")
    hist_behavior = compute_group_behavior(historical_df)
    st.dataframe(hist_behavior.set_index("political_group"), use_container_width=True)

    st.subheader("Recent Change Analysis")
    recent_df = pd.DataFrame()
    try:
        recent_df = get_recent_votes(days=30)
    except Exception as exc:
        st.warning(f"Could not load recent vote data: {exc}")

    if not recent_df.empty:
        try:
            comparison = get_cached_comparison(historical_df, recent_df)
            comparison_summary = comparison.get("summary", {})

            mc_group   = comparison_summary.get("most_changed_group") or "—"
            mc_topic   = comparison_summary.get("most_changed_topic") or "—"
            pol_change = comparison_summary.get("overall_polarization_change")
            pol_label  = f"{pol_change:+.1f} pp" if pol_change is not None else "—"
            pol_delta_color = (
                "normal"
                if pol_change is None or abs(pol_change) < 1.0
                else ("inverse" if pol_change > 0 else "normal")
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Most Changed Group", mc_group)
            m2.metric("Most Changed Topic", mc_topic)
            m3.metric(
                "Polarization Change",
                pol_label,
                delta=pol_label,
                delta_color=pol_delta_color,
            )

            st.subheader("AI Summary")
            if DEMO_MODE:
                st.info("AI Summary is disabled in Demo Mode. Set `DEMO_MODE=false` to enable.")
            else:
                explanation = explain_political_changes(comparison)
                st.write(explanation)

        except Exception as exc:
            st.warning(f"Could not compute recent changes: {exc}")

    st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown(
    "<small style='color:#9ca3af;'>Data: European Parliament Open Data Portal &amp; HowTheyVote.eu</small>",
    unsafe_allow_html=True,
)

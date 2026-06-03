import streamlit as st

st.set_page_config(page_title="EU Vote Tracker - Test", page_icon="🇪🇺")

st.write("## Step 1: Streamlit OK")

try:
    import os, re
    from pathlib import Path
    import pandas as pd
    import plotly.express as px
    st.write("## Step 2: Base imports OK")
except Exception as e:
    st.error(f"Base imports FAILED: {e}")
    st.stop()

try:
    from config import settings
    st.write(f"## Step 3: config OK — DATA_DIR = `{settings.DATA_DIR}`")
except Exception as e:
    st.error(f"config import FAILED: {e}")
    st.stop()

try:
    from eu_dataset_loader import get_eu_votes
    df = get_eu_votes()
    st.write(f"## Step 4: Data loaded OK — {len(df):,} rows, {df['policy_topic'].nunique()} topics")
except Exception as e:
    import traceback
    st.error(f"Data loading FAILED: {e}")
    st.code(traceback.format_exc())
    st.stop()

try:
    from eu_api import fetch_all_votes
    from analysis_agent import analyze_policy, generate_ai_insight
    from recent_data_loader import load_recent_votes
    from political_comparison_engine import compare_behavior, compute_group_behavior
    from political_ai_explainer import explain_political_changes
    st.write("## Step 5: All module imports OK")
except Exception as e:
    import traceback
    st.error(f"Module import FAILED: {e}")
    st.code(traceback.format_exc())
    st.stop()

st.success("✅ All checks passed! The full app should work. Reverting to full version...")

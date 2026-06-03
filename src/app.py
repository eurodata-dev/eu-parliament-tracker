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
    import os
    from pathlib import Path
    from config import settings
    data_dir = Path(settings.DATA_DIR)
    parquet_path = data_dir / "processed" / "eu_votes_real.parquet"
    csv_path     = data_dir / "processed" / "eu_votes_real.csv"
    sample_path  = data_dir / "raw" / "eu_votes_sample.csv"
    st.write(f"**parquet exists:** {parquet_path.exists()} — size: {parquet_path.stat().st_size // 1024} KB" if parquet_path.exists() else f"**parquet:** NOT FOUND at `{parquet_path}`")
    st.write(f"**real CSV exists:** {csv_path.exists()} — size: {csv_path.stat().st_size // 1024} KB" if csv_path.exists() else f"**real CSV:** NOT FOUND")
    st.write(f"**sample CSV exists:** {sample_path.exists()}" )
except BaseException as e:
    st.error(f"File check FAILED: {e}")

try:
    import pandas as pd
    import pyarrow.parquet as pq
    from config import settings
    from pathlib import Path
    parquet_path = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    if parquet_path.exists():
        meta = pq.read_metadata(str(parquet_path))
        st.write(f"## Step 4a: Parquet metadata OK — {meta.num_rows:,} rows, {meta.num_row_groups} row groups")
    else:
        st.write("## Step 4a: Parquet not found — will use CSV fallback")
except BaseException as e:
    import traceback
    st.error(f"Step 4a (parquet metadata) FAILED: {e}")
    st.code(traceback.format_exc())

try:
    from eu_dataset_loader import get_eu_votes
    df = get_eu_votes()
    st.write(f"## Step 4b: Data loaded OK — {len(df):,} rows, {df['policy_topic'].nunique()} topics")
except BaseException as e:
    import traceback
    st.error(f"Step 4b (data load) FAILED: {e}")
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

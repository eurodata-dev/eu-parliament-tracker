import streamlit as st

st.set_page_config(page_title="EU Vote Tracker - Test", page_icon="EU")

st.write("## Step 1: Streamlit OK")

try:
    from pathlib import Path
    import pandas as pd
    import plotly.express as px
    st.write("## Step 2: Base imports OK")
except Exception as e:
    st.error(f"Base imports FAILED: {e}")
    st.stop()

try:
    from config import settings
    st.write(f"## Step 3: config OK")
except Exception as e:
    st.error(f"config import FAILED: {e}")
    st.stop()

try:
    from pathlib import Path
    from config import settings
    p = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    c = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.csv"
    s = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"
    st.write(f"parquet: {p.exists()} {p.stat().st_size//1024}KB" if p.exists() else f"parquet: NOT FOUND {p}")
    st.write(f"csv: {c.exists()} {c.stat().st_size//1024}KB" if c.exists() else "csv: NOT FOUND")
    st.write(f"sample: {s.exists()}")
except BaseException as e:
    st.error(f"File check FAILED: {e}")

try:
    import pyarrow.parquet as pq
    from pathlib import Path
    from config import settings
    p = Path(settings.DATA_DIR) / "processed" / "eu_votes_real.parquet"
    if p.exists():
        m = pq.read_metadata(str(p))
        st.write(f"## Step 4a: parquet meta OK {m.num_rows} rows")
    else:
        st.write("## Step 4a: parquet not found")
except BaseException as e:
    import traceback
    st.error(f"Step 4a FAILED: {e}")
    st.code(traceback.format_exc())

try:
    from eu_dataset_loader import get_eu_votes
    df = get_eu_votes()
    st.write(f"## Step 4b: loaded {len(df)} rows {df['policy_topic'].nunique()} topics")
except BaseException as e:
    import traceback
    st.error(f"Step 4b FAILED: {e}")
    st.code(traceback.format_exc())
    st.stop()

try:
    from eu_api import fetch_all_votes
    from analysis_agent import analyze_policy, generate_ai_insight
    from recent_data_loader import load_recent_votes
    from political_comparison_engine import compare_behavior, compute_group_behavior
    from political_ai_explainer import explain_political_changes
    st.write("## Step 5: All imports OK")
except Exception as e:
    import traceback
    st.error(f"Module import FAILED: {e}")
    st.code(traceback.format_exc())
    st.stop()

st.success("All checks passed!")

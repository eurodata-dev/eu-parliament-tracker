"""
generate_clean_parquet.py
Run locally to produce a compact parquet from the full CSV.
Keeps every unique (member, group, topic, vote, date) combination.
Usage: python src/scripts/generate_clean_parquet.py
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent.parent
CSV  = ROOT / "data" / "processed" / "eu_votes_real.csv"
OUT  = ROOT / "data" / "processed" / "eu_votes_real.parquet"

SCHEMA = ["member_name", "political_group", "policy_topic", "vote", "date"]
CHUNK  = 500_000

if not CSV.exists():
    print(f"ERROR: {CSV} not found"); sys.exit(1)

print(f"Source CSV: {CSV.stat().st_size / 1024**2:.0f} MB")
print("Reading in chunks — deduplicating all 5 columns...")

seen  = set()
parts = []
total = 0

for i, chunk in enumerate(pd.read_csv(CSV, usecols=SCHEMA, chunksize=CHUNK)):
    # Dedup key = all 5 columns
    keys = (chunk["member_name"].astype(str) + "||"
          + chunk["political_group"].astype(str) + "||"
          + chunk["policy_topic"].astype(str) + "||"
          + chunk["vote"].astype(str) + "||"
          + chunk["date"].astype(str))
    new = chunk[~keys.isin(seen)]
    new = new.drop_duplicates(subset=SCHEMA)
    new_keys = (new["member_name"].astype(str) + "||"
              + new["political_group"].astype(str) + "||"
              + new["policy_topic"].astype(str) + "||"
              + new["vote"].astype(str) + "||"
              + new["date"].astype(str)).tolist()
    seen.update(new_keys)
    parts.append(new)
    total += len(new)
    print(f"  chunk {i:>3}: {len(new):>7,} new rows  (running total {total:,})")

print(f"\nConcatenating {total:,} rows...")
df = pd.concat(parts, ignore_index=True)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
for col in ("member_name", "political_group", "policy_topic", "vote"):
    df[col] = df[col].fillna("").astype("category")

print(f"Topics  : {df['policy_topic'].nunique()}")
print(f"MEPs    : {df['member_name'].nunique()}")
print(f"Dates   : {df['date'].min().date()} -> {df['date'].max().date()}")

df.to_parquet(OUT, index=False, engine="pyarrow")
mb = OUT.stat().st_size / 1024**2
print(f"\nSaved -> {OUT}  ({mb:.1f} MB, {len(df):,} rows)")
print("Now run: git add data/processed/eu_votes_real.parquet && git commit -m 'data: full dedup parquet' && git push origin HEAD:main")

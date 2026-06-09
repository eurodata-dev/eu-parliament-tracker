"""
generate_yearly_parquets.py
Splits the full CSV into one parquet per year, fully deduplicated.
Usage: python src/scripts/generate_yearly_parquets.py
"""
import sys
from pathlib import Path
import pandas as pd

ROOT    = Path(__file__).parent.parent.parent
CSV     = ROOT / "data" / "processed" / "eu_votes_real.csv"
OUT_DIR = ROOT / "data" / "processed" / "by_year"
SCHEMA  = ["member_name", "political_group", "policy_topic", "vote", "date"]
CHUNK   = 500_000

if not CSV.exists():
    print(f"ERROR: {CSV} not found"); sys.exit(1)

OUT_DIR.mkdir(exist_ok=True)
print(f"Source CSV: {CSV.stat().st_size / 1024**2:.0f} MB")
print("Reading and splitting by year...")

buckets = {}  # year -> set of seen keys + list of rows

for i, chunk in enumerate(pd.read_csv(CSV, usecols=SCHEMA, chunksize=CHUNK)):
    chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
    chunk["year"] = chunk["date"].dt.year
    for year, grp in chunk.groupby("year", observed=True):
        if pd.isna(year): continue
        year = int(year)
        if year not in buckets:
            buckets[year] = {"seen": set(), "parts": []}
        keys = (grp["member_name"].astype(str) + "||"
              + grp["political_group"].astype(str) + "||"
              + grp["policy_topic"].astype(str) + "||"
              + grp["vote"].astype(str) + "||"
              + grp["date"].astype(str))
        new = grp[~keys.isin(buckets[year]["seen"])].drop_duplicates(subset=SCHEMA)
        new_keys = (new["member_name"].astype(str) + "||"
                  + new["political_group"].astype(str) + "||"
                  + new["policy_topic"].astype(str) + "||"
                  + new["vote"].astype(str) + "||"
                  + new["date"].astype(str)).tolist()
        buckets[year]["seen"].update(new_keys)
        buckets[year]["parts"].append(new.drop(columns=["year"]))
    print(f"  chunk {i:>3} done — years so far: {sorted(buckets.keys())}")

print("\nSaving yearly parquets...")
for year in sorted(buckets.keys()):
    df = pd.concat(buckets[year]["parts"], ignore_index=True)
    for col in ("member_name", "political_group", "policy_topic", "vote"):
        df[col] = df[col].fillna("").astype("category")
    out = OUT_DIR / f"eu_votes_{year}.parquet"
    df.to_parquet(out, index=False, engine="pyarrow")
    kb = out.stat().st_size / 1024
    print(f"  {year}: {len(df):,} rows — {kb:.0f} KB -> {out.name}")

print("\nDone! Now run:")
print("  git add data/processed/by_year/")
print("  git commit -m 'data: yearly parquets full dedup'")
print("  git push origin HEAD:main")

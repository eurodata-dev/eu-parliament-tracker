# EU Parliament Vote Tracker 🇪🇺

A web application for journalists, analysts, and citizens to explore and understand how European Parliament political groups vote on legislation.

**Live demo:** *(add your Streamlit Cloud URL here)*

---

## What it does

Search 4.6 million EP voting records (2019–2026) by topic and instantly see:

- **How each political group voted** — stacked bar chart (FOR / AGAINST / ABSTAIN)
- **Overall result** — did the motion pass or fail?
- **AI-powered analysis** — factual summary of voting patterns via Llama 3 (free)
- **Recent political shifts** — compares the last 30 days against historical behavior
- **Live data** — refreshes from the EU Parliament API on demand and daily via GitHub Actions

---

## Tech stack

| Layer | Technology |
|---|---|
| UI | Python + Streamlit |
| Data | Pandas + PyArrow (Parquet) |
| Charts | Plotly |
| AI Analysis | Groq API (Llama 3, free tier) |
| Live data | HowTheyVote.eu API |
| Automation | GitHub Actions (daily refresh) |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/eu-parliament-tracker.git
cd eu-parliament-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file at the project root:

```
GROQ_API_KEY=your_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com) — no credit card required.

### 4. Run

```bash
python -m streamlit run src/app.py
```

---

## Data sources

- **Historical (2019–2024):** [HowTheyVote.eu](https://howtheyvote.eu) open dataset — processed into Parquet for fast queries
- **Live (recent sessions):** HowTheyVote.eu public API, auto-refreshed daily

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect the repo, set main file to `src/app.py`
4. Add `GROQ_API_KEY` as a secret in the app settings

---

## Project structure

```
├── src/
│   ├── app.py                    # Streamlit UI (main entry point)
│   ├── eu_api.py                 # Data access layer
│   ├── eu_dataset_loader.py      # Loads Parquet dataset
│   ├── ep_live_fetcher.py        # Fetches live EP votes from API
│   ├── analysis_agent.py         # AI analysis via Groq/Llama 3
│   ├── political_comparison_engine.py  # Detects voting shifts
│   └── political_ai_explainer.py # Formats comparison summaries
├── data/
│   ├── processed/                # eu_votes_real.parquet (fast)
│   └── recent/                   # Live vote CSVs
├── scripts/
│   └── load_real_votes.py        # CSV → Parquet ingestion pipeline
├── .github/workflows/
│   └── update_votes.yml          # Daily auto-refresh via GitHub Actions
└── requirements.txt
```

---

*Built with Python, Streamlit, and open EU Parliament data.*

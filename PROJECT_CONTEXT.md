# EU Policy Intelligence Agent — Project Context

## Objective

Build an AI-powered system that analyzes European Parliament voting data
and generates political insights. Progressively evolving from CSV mock data
toward live EP Open Data Portal integration.

---

## Project Architecture

```
src/
├── app.py               # Streamlit dashboard (main UI)
├── eu_api.py            # API boundary layer — single data-fetch entry point
├── data_loader.py       # Low-level data access (CSV → future: EP REST API)
├── analysis_agent.py    # Vote aggregation + AI insight generation (Ollama/mistral)
├── config.py            # Settings and environment variables
├── prompts.py           # Prompt templates
├── main.py              # Legacy CLI interface
└── download_sample_data.py  # Script that generated the CSV dataset

data/
├── raw/
│   └── eu_votes_sample.csv  # Primary dataset (32 rows, 6 topics, 6 groups)
└── processed/               # Reserved for cleaned/enriched data
```

### Layer responsibilities

| File | Role |
|---|---|
| `eu_api.py` | Public interface for all vote data. Callers never touch data_loader directly. |
| `data_loader.py` | Reads CSV; will be replaced by EP API calls. |
| `analysis_agent.py` | Aggregates votes; calls Ollama for AI narrative. |
| `app.py` | Streamlit UI — KPIs, charts, topic search, AI insights. |

---

## Data Layer

### Current source
- File: `data/raw/eu_votes_sample.csv`
- 32 rows covering 6 policy topics and 6 political groups
- Real MEP names (Axel Voss, Brando Benifei, Manfred Weber, Roberta Metsola, etc.)

### Columns
| Column | Type | Values |
|---|---|---|
| member_name | str | Full MEP name |
| political_group | str | EPP, S&D, Renew, Greens/EFA, ECR, ID |
| policy_topic | str | AI Act, Climate Policy, Migration Policy, Digital Services Act, Green Deal, Cybersecurity |
| vote | str | FOR, AGAINST, ABSTAIN |
| date | datetime | Actual plenary vote dates |

### Fallback chain
```
eu_api.fetch_mock_eu_votes()
    └── data_loader.load_votes()
            ├── CSV exists  →  read CSV
            └── CSV missing →  get_mock_votes() (hardcoded fallback)
```

### Future: EP Open Data Portal
- Base URL: https://data.europarl.europa.eu/api/v2/
- Target endpoint: /votes
- Integration point: replace body of `fetch_mock_eu_votes()` in `eu_api.py`
- `data_loader.fetch_url()` is already wired for HTTP calls

---

## AI Layer

- Runtime: Ollama (local LLM server)
- Model: mistral
- Endpoint: http://localhost:11434/api/generate
- Timeout: 180 seconds
- Error handling: connection errors, timeouts, HTTP errors, malformed JSON
  all return readable strings displayed as `st.warning()` in Streamlit

### To activate
```
ollama serve
ollama pull mistral
```

### Future: Claude / Anthropic
Commented-out stub already present in `analysis_agent.py`:
```python
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-sonnet-4-6", api_key=settings.ANTHROPIC_API_KEY)
# return llm.invoke(prompt).content
```

---

## Streamlit Dashboard (app.py)

### Sections
1. **KPI row** — Total votes · Policy topics · Political groups · % FOR votes
2. **Global Vote Analytics**
   - Overall FOR / AGAINST / ABSTAIN distribution (bar chart)
   - Total votes by political group (bar chart)
   - Political group ranking table (FOR, AGAINST, ABSTAIN, Total)
3. **Topic Analysis**
   - Free-text search with 3-pass intelligent matching (exact → substring → word-overlap)
   - Per-topic voting summary table
   - Per-topic vote distribution chart
   - AI-generated insight via mistral

### Run
```
streamlit run src/app.py
```

---

## eu_api.py — API Boundary Layer

### Purpose
Single stable entry point for all vote data. When real API replaces CSV,
only the internals of these two functions change — no callers are affected.

### Functions

**`search_policy_topic(query: str) -> str | None`**
- Normalizes the query
- 3-pass matching: exact → substring → word-overlap
- Returns the exact topic label or None

**`fetch_mock_eu_votes(query: str) -> pd.DataFrame`**
- Calls `search_policy_topic()` then `load_votes()`
- Returns filtered DataFrame with guaranteed column schema
- Returns empty DataFrame (correct columns) if no match
- Contains commented-out EP API call showing exact replacement point

---

## Completed Milestones

| Date | Milestone |
|---|---|
| 2026-05-07 | Created `data/raw/eu_votes_sample.csv` with 32 realistic rows |
| 2026-05-07 | Created `src/download_sample_data.py` |
| 2026-05-08 | Updated `data_loader.py`: CSV as primary source, mock as fallback |
| 2026-05-08 | Built full Streamlit dashboard in `app.py` (KPIs, global charts, topic analysis) |
| 2026-05-08 | Switched AI model from llama3 → mistral, timeout 60s → 180s, improved error messages |
| 2026-05-08 | Created `src/eu_api.py`: future-proof API boundary layer |

---

## Next Steps

1. Wire `app.py` to call `eu_api.fetch_mock_eu_votes()` instead of `load_votes()` directly
2. Connect to live EP Open Data Portal API (replace body of `fetch_mock_eu_votes()`)
3. Switch AI insight from Ollama/mistral to Claude API (stub already in analysis_agent.py)
4. Deploy as portfolio project

---

## Notes

- Topic matching is case-insensitive and supports partial queries
- System is modular: each layer can be replaced independently
- Do not break existing function signatures when updating
- `get_mock_votes()` must remain in `data_loader.py` as emergency fallback

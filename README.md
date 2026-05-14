# EU Policy Intelligence Agent

A Python-based intelligence agent for analyzing EU policy documents and regulations.

## Project Structure

```
eu-policy-intelligence-agent/
├── src/
│   ├── main.py            # Entry point
│   ├── config.py          # Settings and environment config
│   ├── data_loader.py     # CSV and API data loading
│   ├── analysis_agent.py  # LangChain-based analysis agent
│   └── prompts.py         # Prompt templates
├── data/                  # Local data files
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (create a `.env` file):
   ```
   ANTHROPIC_API_KEY=your_key_here
   ENV=development
   ```

## Run

```bash
cd src
python main.py
```

## Notes

- Streamlit is included in dependencies for future UI integration.
- Add a `.env` file at the project root; use `python-dotenv` to load it.

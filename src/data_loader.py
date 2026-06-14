import requests
import pandas as pd
from pathlib import Path
from config import settings


def load_csv(filename: str) -> pd.DataFrame:
    path = Path(settings.DATA_DIR) / filename
    return pd.read_csv(path)


def fetch_url(url: str, params: dict | None = None) -> dict:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_mock_votes() -> pd.DataFrame:
    """Return a mock DataFrame of European Parliament voting records.

    Columns:
        member_name     (str)              Full name of the MEP.
        political_group (str)              EP political group abbreviation
                                           (EPP, S&D, Renew, Greens/EFA, ID, ECR).
        policy_topic    (str)              High-level policy area.
        vote            (str)              One of: FOR | AGAINST | ABSTAIN.
        date            (pd.Timestamp)     Date of the plenary vote.

    Data source: mock — for live data see the EP Open Data Portal
    (https://data.europarl.europa.eu).
    """
    records = [
        # --- AI Act (voted March 2024) ---
        {"member_name": "Dragos Tudorache",    "political_group": "Renew",      "policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
        {"member_name": "Brando Benifei",      "political_group": "S&D",        "policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
        {"member_name": "Peter Kofod",         "political_group": "ID",         "policy_topic": "AI Act",             "vote": "AGAINST", "date": "2024-03-13"},

        # --- Climate Policy (voted June 2023) ---
        {"member_name": "Mohammed Chahim",     "political_group": "S&D",        "policy_topic": "Climate Policy",     "vote": "FOR",     "date": "2023-06-22"},
        {"member_name": "Bas Eickhout",        "political_group": "Greens/EFA", "policy_topic": "Climate Policy",     "vote": "FOR",     "date": "2023-06-22"},
        {"member_name": "Alexandr Vondra",     "political_group": "ECR",        "policy_topic": "Climate Policy",     "vote": "AGAINST", "date": "2023-06-22"},

        # --- Digital Services Act (voted July 2022) ---
        {"member_name": "Christel Schaldemose", "political_group": "S&D",       "policy_topic": "Digital Services Act", "vote": "FOR",   "date": "2022-07-05"},
        {"member_name": "Andreas Schwab",      "political_group": "EPP",        "policy_topic": "Digital Services Act", "vote": "FOR",   "date": "2022-07-05"},
        {"member_name": "Marcel de Graaff",    "political_group": "ID",         "policy_topic": "Digital Services Act", "vote": "AGAINST", "date": "2022-07-05"},

        # --- Migration Policy (voted April 2024) ---
        {"member_name": "Roberta Metsola",     "political_group": "EPP",        "policy_topic": "Migration Policy",   "vote": "FOR",     "date": "2024-04-10"},
        {"member_name": "Tineke Strik",        "political_group": "Greens/EFA", "policy_topic": "Migration Policy",   "vote": "AGAINST", "date": "2024-04-10"},
        {"member_name": "Fabrice Leggeri",     "political_group": "ID",         "policy_topic": "Migration Policy",   "vote": "ABSTAIN", "date": "2024-04-10"},
    ]

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_votes() -> pd.DataFrame:
    """Load European Parliament voting records into a DataFrame.

    Primary source: data/raw/eu_votes_sample.csv (CSV dataset).
    Fallback: get_mock_votes() if the CSV is missing.

    Later this CSV will be replaced by live EU Parliament API calls:
        # response = fetch_url(
        # "https://data.europarl.europa.eu/api/v2/votes",
        # params={"format": "application/json", "limit": 200},
        # )
        # return pd.DataFrame(response["data"])

    Returns:
        pd.DataFrame with columns: member_name, political_group,
        policy_topic, vote, date.
    """
    # CSV is now the primary data source - replaces hardcoded mock data.
    csv_path = Path(settings.DATA_DIR) / "raw" / "eu_votes_sample.csv"

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df["date"] = pd.to_datetime(df["date"])
        return df

    # CSV not found - fall back to mock data for safety.
    return get_mock_votes()

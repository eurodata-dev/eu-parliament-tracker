# Step 1 of real data integration: manually curated realistic CSV dataset.
# This replaces the in-memory mock data in data_loader.py.
# Later this script will be replaced by live EU Parliament API calls
# (e.g. via the VoteWatch API or the official EP Open Data portal).

import pandas as pd
import os

# fmt: off
ROWS = [
    # AI Act
    {"member_name": "Axel Voss",            "political_group": "EPP",       "policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Brando Benifei",       "political_group": "S&D",       "policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Dragoș Tudorache",     "political_group": "Renew",     "policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Kim Van Sparrentak",   "political_group": "Greens/EFA","policy_topic": "AI Act",             "vote": "FOR",     "date": "2024-03-13"},
    {"member_name": "Annalisa Tardino",     "political_group": "ID",        "policy_topic": "AI Act",             "vote": "AGAINST", "date": "2024-03-13"},
    {"member_name": "Kosma Złotowski",      "political_group": "ECR",       "policy_topic": "AI Act",             "vote": "ABSTAIN", "date": "2024-03-13"},

    # Climate Policy
    {"member_name": "Peter Liese",          "political_group": "EPP",       "policy_topic": "Climate Policy",     "vote": "AGAINST", "date": "2023-04-18"},
    {"member_name": "Mohammed Chahim",      "political_group": "S&D",       "policy_topic": "Climate Policy",     "vote": "FOR",     "date": "2023-04-18"},
    {"member_name": "Pascal Canfin",        "political_group": "Renew",     "policy_topic": "Climate Policy",     "vote": "FOR",     "date": "2023-04-18"},
    {"member_name": "Michael Bloss",        "political_group": "Greens/EFA","policy_topic": "Climate Policy",     "vote": "FOR",     "date": "2023-04-18"},
    {"member_name": "Marco Zanni",          "political_group": "ID",        "policy_topic": "Climate Policy",     "vote": "AGAINST", "date": "2023-04-18"},
    {"member_name": "Bogdan Rzońca",        "political_group": "ECR",       "policy_topic": "Climate Policy",     "vote": "AGAINST", "date": "2023-04-18"},

    # Migration Policy
    {"member_name": "Roberta Metsola",      "political_group": "EPP",       "policy_topic": "Migration Policy",   "vote": "FOR",     "date": "2023-09-20"},
    {"member_name": "Birgit Sippel",        "political_group": "S&D",       "policy_topic": "Migration Policy",   "vote": "AGAINST", "date": "2023-09-20"},
    {"member_name": "Sophie in 't Veld",    "political_group": "Renew",     "policy_topic": "Migration Policy",   "vote": "AGAINST", "date": "2023-09-20"},
    {"member_name": "Erik Marquardt",       "political_group": "Greens/EFA","policy_topic": "Migration Policy",   "vote": "AGAINST", "date": "2023-09-20"},
    {"member_name": "Matteo Salvini",       "political_group": "ID",        "policy_topic": "Migration Policy",   "vote": "FOR",     "date": "2023-09-20"},
    {"member_name": "Nicola Procaccini",    "political_group": "ECR",       "policy_topic": "Migration Policy",   "vote": "FOR",     "date": "2023-09-20"},

    # Digital Services Act
    {"member_name": "Andreas Schwab",       "political_group": "EPP",       "policy_topic": "Digital Services Act","vote": "FOR",    "date": "2022-07-05"},
    {"member_name": "Christel Schaldemose", "political_group": "S&D",       "policy_topic": "Digital Services Act","vote": "FOR",    "date": "2022-07-05"},
    {"member_name": "Dita Charanzová",      "political_group": "Renew",     "policy_topic": "Digital Services Act","vote": "FOR",    "date": "2022-07-05"},
    {"member_name": "Alexandra Geese",      "political_group": "Greens/EFA","policy_topic": "Digital Services Act","vote": "FOR",    "date": "2022-07-05"},
    {"member_name": "Ivan Štefanec",        "political_group": "ECR",       "policy_topic": "Digital Services Act","vote": "ABSTAIN","date": "2022-07-05"},

    # Green Deal
    {"member_name": "Manfred Weber",        "political_group": "EPP",       "policy_topic": "Green Deal",         "vote": "AGAINST", "date": "2023-06-22"},
    {"member_name": "Iratxe García Pérez",  "political_group": "S&D",       "policy_topic": "Green Deal",         "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Nathalie Colin-Oesterlé","political_group": "Renew",   "policy_topic": "Green Deal",         "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Bas Eickhout",         "political_group": "Greens/EFA","policy_topic": "Green Deal",         "vote": "FOR",     "date": "2023-06-22"},
    {"member_name": "Jordan Bardella",      "political_group": "ID",        "policy_topic": "Green Deal",         "vote": "AGAINST", "date": "2023-06-22"},

    # Cybersecurity
    {"member_name": "Bart Groothuis",       "political_group": "Renew",     "policy_topic": "Cybersecurity",      "vote": "FOR",     "date": "2022-11-10"},
    {"member_name": "Maria Walsh",          "political_group": "EPP",       "policy_topic": "Cybersecurity",      "vote": "FOR",     "date": "2022-11-10"},
    {"member_name": "Lukas Mandl",          "political_group": "ECR",       "policy_topic": "Cybersecurity",      "vote": "FOR",     "date": "2022-11-10"},
    {"member_name": "Hannah Neumann",       "political_group": "Greens/EFA","policy_topic": "Cybersecurity",      "vote": "ABSTAIN", "date": "2022-11-10"},
]
# fmt: on

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw", "eu_votes_sample.csv"
)


def main():
    df = pd.DataFrame(ROWS)
    df["date"] = pd.to_datetime(df["date"])
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {os.path.abspath(OUTPUT_PATH)}")


if __name__ == "__main__":
    main()

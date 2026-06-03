import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Try to find .env in: project root, src/, or current working directory
for _candidate in [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent / ".env",
    Path(".env"),
]:
    if _candidate.exists():
        load_dotenv(dotenv_path=_candidate, override=True)
        break

# Streamlit Cloud: inject st.secrets into os.environ so the rest of the code
# can use os.getenv() regardless of where it's running.
try:
    import streamlit as st
    for _key, _val in st.secrets.items():
        if isinstance(_val, str) and _key not in os.environ:
            os.environ[_key] = _val
except Exception:
    pass  # Not running inside Streamlit, or no secrets configured — that's fine.


@dataclass
class Settings:
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    DATA_DIR: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "..", "data"))


settings = Settings()

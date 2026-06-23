import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

for _candidate in [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent / ".env",
    Path(".env"),
]:
    if _candidate.exists():
        load_dotenv(dotenv_path=_candidate, override=True)
        break


@dataclass
class Settings:
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    DATA_DIR: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "..", "data"))


settings = Settings()

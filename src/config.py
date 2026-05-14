import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    DATA_DIR: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "..", "data"))


settings = Settings()

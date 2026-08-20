from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(slots=True)
class Settings:
    app_name: str = "BistroBot"
    demo_business_name: str = "Maple & Thyme Bistro"
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'chatbot.db'}")
    faq_path: Path = Path(os.getenv("FAQ_PATH", BASE_DIR / "data" / "faqs.json"))
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    cors_origins: list[str] = None

    def __post_init__(self) -> None:
        raw_origins = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


settings = Settings()

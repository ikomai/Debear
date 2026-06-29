"""Application configuration loaded from the .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "")
    ids: set[int] = set()
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if chunk.isdigit():
            ids.add(int(chunk))
    return ids


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    admin_ids: set[int] = field(default_factory=_admin_ids)

    db_engine: str = os.getenv("DB_ENGINE", "sqlite").lower()
    sqlite_path: str = os.getenv("SQLITE_PATH", "bot.db")

    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_db: str = os.getenv("MYSQL_DB", "")

    # Full database URL (used by hosting platforms like Fly.io). Takes priority.
    database_url_env: str = os.getenv("DATABASE_URL", "")

    storage_dir: Path = BASE_DIR / os.getenv("STORAGE_DIR", "storage")

    @property
    def database_url(self) -> str:
        # A platform-provided DATABASE_URL wins (e.g. Fly.io Postgres).
        if self.database_url_env:
            url = self.database_url_env
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            # asyncpg doesn't accept libpq's "?sslmode=" query param; drop it.
            # Fly's internal .flycast connection doesn't use SSL.
            if "?" in url:
                url = url.split("?", 1)[0]
            return url
        if self.db_engine == "mysql":
            return (
                f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
                f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
            )
        # default: local SQLite, runs without any setup
        return f"sqlite+aiosqlite:///{(BASE_DIR / self.sqlite_path).as_posix()}"

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
(settings.storage_dir / "documents").mkdir(exist_ok=True)
(settings.storage_dir / "pdf").mkdir(exist_ok=True)

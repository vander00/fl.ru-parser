from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class BotConfig:
    token: str
    chat_id: int
    poll_interval: float = 300.0
    max_pages: int = 2
    categories: list[str] | None = None
    db_path: str = "flparser.db"
    answer_unknowns: bool = False
    kind: int = 1
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> BotConfig:
        load_dotenv()

        token: str = _require("BOT_TOKEN")
        chat_id: int = _require_int("TELEGRAM_CHAT_ID")
        poll_interval: float = float(os.getenv("POLL_INTERVAL_SECONDS", "300"))
        max_pages: int = int(os.getenv("MAX_PAGES", "2"))
        categories: list[str] | None = os.getenv("CATEGORIES", "").split() or None
        db_path: str = os.getenv("DB_PATH", "flparser.db")
        answer_unknowns: bool = False if os.getenv("ANSWER_UNKNOWNS") is None else True
        kind: int = int(os.getenv("KIND", "1"))
        log_level: str = os.getenv("LOG_LEVEL", "INFO")

        if poll_interval <= 0:
            raise ValueError("POLL_INTERVAL_SECONDS must be > 0")
        if max_pages < 1:
            raise ValueError("MAX_PAGES must be >= 1")

        return cls(
            token=token,
            chat_id=chat_id,
            poll_interval=poll_interval,
            max_pages=max_pages,
            categories=categories,
            db_path=db_path,
            answer_unknowns=answer_unknowns,
            kind=kind,
            log_level=log_level,
        )


def _require(name: str) -> str:
    value: str | None = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def _require_int(name: str) -> int:
    raw: str = _require(name)
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be an integer (number"
        ) from exc

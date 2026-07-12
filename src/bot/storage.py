from __future__ import annotations

import logging
import sqlite3
import time

from ..schemas import ArchivedProject, ProjectInfo

logger: logging.Logger = logging.getLogger(__name__)

RETENTION_SECONDS: int = 30 * 24 * 60 * 60  # The time to reset all the DB
# Probably should move it to the config

_COLUMNS: tuple[str, ...] = (
    "chat_id",
    "project_id",
    "name",
    "url",
    "budget",
    "posted",
    "first_seen_at",
    "last_seen_at",
)


# It would be better the DB to be async but actually it doesn't make a lot of sense because the bot is likely not popular
# so maybe the class gotta be rewriten later
class SeenStore:
    def __init__(self, path: str, retention_seconds: int = RETENTION_SECONDS) -> None:
        self._retention: int = retention_seconds
        self._conn: sqlite3.Connection = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        existing: set[str] = {
            row["name"]
            for row in self._conn.execute("PRAGMA table_info(seen_projects)")
        }
        if existing and not set(_COLUMNS).issubset(existing):
            logger.info("Migrating seen_projects to the current schema")
            self._conn.execute("DROP TABLE seen_projects")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_projects (
                chat_id       INTEGER NOT NULL,
                project_id    TEXT    NOT NULL,
                name          TEXT    NOT NULL DEFAULT '',
                url           TEXT    NOT NULL DEFAULT '',
                budget        TEXT    NOT NULL DEFAULT '',
                posted        TEXT    NOT NULL DEFAULT '',
                first_seen_at REAL    NOT NULL,
                last_seen_at  REAL    NOT NULL,
                PRIMARY KEY (chat_id, project_id)
            )
            """
        )
        self._conn.commit()

    def has_any(self, chat_id: int) -> bool:
        cursor: sqlite3.Cursor = self._conn.execute(
            "SELECT 1 FROM seen_projects WHERE chat_id = ? LIMIT 1", (chat_id,)
        )
        return cursor.fetchone() is not None

    def known(self, chat_id: int, project_ids: list[str]) -> set[str]:
        if not project_ids:
            return set()
        placeholders: str = ",".join("?" * len(project_ids))
        cursor: sqlite3.Cursor = self._conn.execute(
            f"SELECT project_id FROM seen_projects "
            f"WHERE chat_id = ? AND project_id IN ({placeholders})",
            (chat_id, *project_ids),
        )
        return {row["project_id"] for row in cursor.fetchall()}

    def remember(self, chat_id: int, projects: list[ProjectInfo]) -> None:
        if not projects:
            return
        now: float = time.time()
        self._conn.executemany(
            "INSERT INTO seen_projects "
            "(chat_id, project_id, name, url, budget, posted, "
            " first_seen_at, last_seen_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(chat_id, project_id) DO UPDATE SET "
            "  name = excluded.name, url = excluded.url, "
            "  budget = excluded.budget, posted = excluded.posted, "
            "  last_seen_at = excluded.last_seen_at",
            [
                (
                    chat_id,
                    project.id,
                    project.name,
                    project.url,
                    project.budget,
                    project.posted,
                    now,
                    now,
                )
                for project in projects
            ],
        )
        self._conn.commit()

    def recent(self, chat_id: int, limit: int = 15) -> list[ArchivedProject]:
        cursor: sqlite3.Cursor = self._conn.execute(
            "SELECT project_id, name, url, budget, posted, first_seen_at "
            "FROM seen_projects WHERE chat_id = ? "
            "ORDER BY first_seen_at DESC LIMIT ?",
            (chat_id, limit),
        )
        return [
            ArchivedProject(
                project_id=row["project_id"],
                name=row["name"],
                url=row["url"],
                budget=row["budget"],
                posted=row["posted"],
                first_seen_at=row["first_seen_at"],
            )
            for row in cursor.fetchall()
        ]

    def purge_expired(self) -> int:
        cutoff: float = time.time() - self._retention
        cursor: sqlite3.Cursor = self._conn.execute(
            "DELETE FROM seen_projects WHERE last_seen_at < ?", (cutoff,)
        )
        self._conn.commit()
        removed: int = cursor.rowcount
        if removed:
            logger.info("Purged %s seen-project rows older than 30 days", removed)
        return removed

    def close(self) -> None:
        self._conn.close()

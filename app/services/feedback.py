"""Visitors' thumbs up/down on the assistant's answers, kept in a small SQLite file."""

import asyncio
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass
from datetime import timedelta

_SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
    visitor    TEXT NOT NULL,
    run_id     TEXT NOT NULL,
    rating     TEXT NOT NULL CHECK (rating IN ('up', 'down')),
    created_at REAL NOT NULL,
    PRIMARY KEY (visitor, run_id)
)
"""


@dataclass(frozen=True)
class Feedback:
    run_id: str
    rating: str
    created_at: float


class FeedbackStore:
    """One rating per visitor per answer; rating the same answer again replaces the earlier one.

    `run_id` is the ID logpose records on the answer's trace, which is how a rating is matched
    to its question and answer. `visitor` is a hash of the session ID, never the ID itself.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        with closing(self._connect()) as connection, connection:
            connection.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path, timeout=5)

    def _record(self, visitor: str, run_id: str, rating: str) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO feedback (visitor, run_id, rating, created_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT (visitor, run_id) DO UPDATE SET "
                "rating = excluded.rating, created_at = excluded.created_at",
                (visitor, run_id, rating, time.time()),
            )

    def _purge(self, cutoff: float) -> int:
        with closing(self._connect()) as connection, connection:
            return connection.execute(
                "DELETE FROM feedback WHERE created_at < ?", (cutoff,)
            ).rowcount

    def all(self) -> list[Feedback]:
        """Every stored rating, oldest first."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT run_id, rating, created_at FROM feedback ORDER BY created_at"
            ).fetchall()
        return [Feedback(run_id=row[0], rating=row[1], created_at=row[2]) for row in rows]

    async def record(self, visitor: str, run_id: str, rating: str) -> None:
        await asyncio.to_thread(self._record, visitor, run_id, rating)

    async def purge(self, older_than: timedelta) -> int:
        """Delete ratings older than `older_than`; returns how many were removed."""
        return await asyncio.to_thread(self._purge, time.time() - older_than.total_seconds())

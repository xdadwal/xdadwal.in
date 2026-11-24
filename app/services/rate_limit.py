"""In-memory request limits for the public chat endpoint (single-process deployment)."""

import ipaddress
import math
import time
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

_SWEEP_EVERY = 1000


def _client_key(ip: str) -> str:
    """One key per client: an IPv6 client controls a whole /64, so limit that, not one address."""
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    if address.version == 6:
        return str(ipaddress.ip_network(f"{address}/64", strict=False))
    return ip


class RateLimiter:
    """A sliding window per client IP plus a ceiling on total requests per UTC day.

    A limit of 0 turns that limit off.
    """

    def __init__(
        self,
        per_ip: int,
        window_seconds: int,
        per_day: int,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._per_ip = per_ip
        self._window = window_seconds
        self._per_day = per_day
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._day = ""
        self._day_count = 0
        self._calls = 0

    def check(self, ip: str) -> int | None:
        """Count the request and return None if allowed, else the seconds to wait (>= 1)."""
        now = self._clock()
        self._calls += 1
        if self._calls % _SWEEP_EVERY == 0:
            self._sweep(now)

        today = datetime.fromtimestamp(now, UTC)
        day = today.date().isoformat()
        if day != self._day:
            self._day, self._day_count = day, 0
        if self._per_day and self._day_count >= self._per_day:
            midnight = datetime.combine(today.date() + timedelta(days=1), datetime.min.time(), UTC)
            return max(1, math.ceil(midnight.timestamp() - now))

        if self._per_ip:
            hits = self._hits.setdefault(_client_key(ip), deque())
            self._expire(hits, now)
            if len(hits) >= self._per_ip:
                return max(1, math.ceil(hits[0] + self._window - now))
            hits.append(now)

        self._day_count += 1
        return None

    def _expire(self, hits: deque[float], now: float) -> None:
        while hits and hits[0] <= now - self._window:
            hits.popleft()

    def _sweep(self, now: float) -> None:
        for ip in list(self._hits):
            self._expire(self._hits[ip], now)
            if not self._hits[ip]:
                del self._hits[ip]

"""In-memory rate limiting helpers for intake endpoints."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Lock
from time import time

from fastapi import HTTPException, Request, status


@dataclass(slots=True)
class InMemoryRateLimiter:
    """A simple per-key sliding window limiter for demo-safe intake protection."""

    max_requests: int
    window_seconds: int
    clock: Callable[[], float] = time
    _events: dict[str, deque[float]] = field(default_factory=lambda: defaultdict(deque))
    _lock: Lock = field(default_factory=Lock)

    def check(self, key: str) -> int | None:
        now = self.clock()
        window_start = now - self.window_seconds

        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] <= window_start:
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                retry_after = max(1, int(bucket[0] + self.window_seconds - now))
                return retry_after

            bucket.append(now)

        return None


def get_client_rate_limit_key(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client is not None and request.client.host:
        return request.client.host

    return "unknown"


def enforce_rate_limit(request: Request) -> None:
    limiter = getattr(request.app.state, "intake_rate_limiter", None)
    if limiter is None:
        return

    key = get_client_rate_limit_key(request)
    retry_after = limiter.check(key)
    if retry_after is None:
        return

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded",
        headers={"Retry-After": str(retry_after)},
    )

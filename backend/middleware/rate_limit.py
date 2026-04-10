from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException

# In-memory rate limiter: team_id -> deque of timestamps
_analysis_timestamps: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=20))

ANALYSIS_LIMIT = 20  # max analyses per hour per team
ANALYSIS_WINDOW = 3600  # 1 hour in seconds


def check_analysis_rate_limit(team_id: str) -> None:
    """Raise 429 if team exceeds 20 analyses per hour."""
    now = time.monotonic()
    timestamps = _analysis_timestamps[team_id]

    # Remove expired entries
    while timestamps and now - timestamps[0] > ANALYSIS_WINDOW:
        timestamps.popleft()

    if len(timestamps) >= ANALYSIS_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {ANALYSIS_LIMIT} analyses per hour per team",
        )

    timestamps.append(now)

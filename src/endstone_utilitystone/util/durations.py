from __future__ import annotations

import math
import re
import time

UNIT_SECONDS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
    "mo": 2629800,
    "y": 31557600,
}

PERMANENT_TOKENS = frozenset({"perm", "permanent", "forever", "never", "inf", "infinite"})
DURATION_PATTERN = re.compile(r"(\d+)(mo|[smhdwy])")


def parseDuration(text: str | None) -> float | None:
    if not text:
        return None

    token = "".join(str(text).split()).lower()
    if not token:
        return None

    if token in PERMANENT_TOKENS:
        return math.inf

    if token.isdigit():
        minutes = int(token)
        return float(minutes * 60) if minutes > 0 else None

    total = 0.0
    remaining = token
    while remaining:
        match = DURATION_PATTERN.match(remaining)
        if match is None:
            return None
        total += int(match.group(1)) * UNIT_SECONDS[match.group(2)]
        remaining = remaining[match.end() :]

    return total if total > 0 else None


def formatDuration(seconds: float | None, precision: int = 2) -> str:
    if seconds is None:
        return "unknown"
    if seconds == math.inf:
        return "permanent"

    remaining = int(max(0.0, seconds))
    if remaining < 1:
        return "moments"

    pieces = []
    for suffix, size in (("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        if remaining < size:
            continue
        value, remaining = divmod(remaining, size)
        pieces.append(f"{value}{suffix}")
        if len(pieces) >= precision:
            break

    return " ".join(pieces)


def formatTimestamp(stamp: float | None) -> str:
    if not stamp:
        return "never"
    return time.strftime("%d %b %Y at %H:%M", time.localtime(stamp))

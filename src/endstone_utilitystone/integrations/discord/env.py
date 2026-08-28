from __future__ import annotations

import os
from pathlib import Path

QUOTES = ("'", '"')


def parseEnvText(text: str) -> dict:
    values = {}

    for rawLine in text.splitlines():
        line = rawLine.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].lstrip()

        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in QUOTES:
            value = value[1:-1]
        else:
            marker = value.find(" #")
            if marker >= 0:
                value = value[:marker].rstrip()

        values[key] = value

    return values


def readEnvFile(path: Path) -> dict:
    try:
        if not path.is_file():
            return {}
        return parseEnvText(path.read_text(encoding="utf-8"))
    except OSError:
        return {}


def loadEnvironment(paths) -> dict:
    values = {}

    for path in paths:
        for key, value in readEnvFile(Path(path)).items():
            values.setdefault(key, value)

    for key in list(values.keys()):
        override = os.environ.get(key)
        if override:
            values[key] = override

    for key in ("DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_ID"):
        if key not in values and os.environ.get(key):
            values[key] = os.environ[key]

    return values

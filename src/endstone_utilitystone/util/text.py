from __future__ import annotations

SECTION = "\u00a7"
AMPERSAND = "&"
VALID_CODES = frozenset("0123456789abcdefghijmnpqstuvklor")


def colorize(text: str) -> str:
    if not text or AMPERSAND not in text:
        return text

    pieces = []
    index = 0
    length = len(text)
    while index < length:
        character = text[index]
        if character != AMPERSAND or index + 1 >= length:
            pieces.append(character)
            index += 1
            continue

        following = text[index + 1]
        if following == AMPERSAND:
            pieces.append(AMPERSAND)
            index += 2
            continue

        if following.lower() in VALID_CODES:
            pieces.append(SECTION)
            pieces.append(following.lower())
            index += 2
            continue

        pieces.append(character)
        index += 1

    return "".join(pieces)


def stripColors(text: str) -> str:
    if not text or SECTION not in text:
        return text

    pieces = []
    index = 0
    length = len(text)
    while index < length:
        if text[index] == SECTION and index + 1 < length:
            index += 2
            continue
        pieces.append(text[index])
        index += 1

    return "".join(pieces)


def shorten(text: str, limit: int) -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    return text[: max(1, limit - 3)] + "..."


def joinNames(names, empty: str = "none") -> str:
    ordered = sorted(names, key=str.lower)
    if not ordered:
        return empty
    return ", ".join(ordered)

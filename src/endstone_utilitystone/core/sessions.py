from __future__ import annotations

import time


class PlayerSession:
    __slots__ = (
        "uniqueId",
        "key",
        "name",
        "joinedAt",
        "lastActivity",
        "lastPlaytimeSync",
        "lastSample",
        "isAfk",
        "afkSince",
        "afkReason",
        "replyTarget",
        "backHistory",
        "cooldowns",
    )

    def __init__(self, player, now: float):
        self.uniqueId = player.unique_id
        self.key = str(player.unique_id)
        self.name = player.name
        self.joinedAt = now
        self.lastActivity = now
        self.lastPlaytimeSync = now
        self.lastSample = None
        self.isAfk = False
        self.afkSince = 0.0
        self.afkReason = ""
        self.replyTarget = None
        self.backHistory = []
        self.cooldowns = {}

    def touch(self, now: float | None = None) -> None:
        self.lastActivity = now if now is not None else time.time()

    def pushBack(self, payload, limit: int) -> None:
        self.backHistory.append(payload)
        while len(self.backHistory) > limit:
            self.backHistory.pop(0)

    def popBack(self):
        if not self.backHistory:
            return None
        return self.backHistory.pop()

    def cooldownRemaining(self, key: str, now: float) -> float:
        expiry = self.cooldowns.get(key)
        if expiry is None or expiry <= now:
            return 0.0
        return expiry - now

    def startCooldown(self, key: str, seconds: float, now: float) -> None:
        if seconds > 0.0:
            self.cooldowns[key] = now + seconds


class SessionRegistry:
    def __init__(self):
        self._byId: dict = {}
        self._byName: dict = {}

    def open(self, player) -> PlayerSession:
        session = PlayerSession(player, time.time())
        self._byId[session.uniqueId] = session
        self._byName[session.name.lower()] = session
        return session

    def close(self, player) -> PlayerSession | None:
        session = self._byId.pop(player.unique_id, None)
        if session is not None:
            self._byName.pop(session.name.lower(), None)
        return session

    def of(self, player) -> PlayerSession | None:
        return self._byId.get(player.unique_id)

    def byId(self, uniqueId) -> PlayerSession | None:
        return self._byId.get(uniqueId)

    def byName(self, name: str) -> PlayerSession | None:
        return self._byName.get(name.lower())

    def all(self):
        return list(self._byId.values())

    def clear(self) -> None:
        self._byId.clear()
        self._byName.clear()

    @property
    def count(self) -> int:
        return len(self._byId)

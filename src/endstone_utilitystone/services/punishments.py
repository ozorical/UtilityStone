from __future__ import annotations

import math
import time
from datetime import datetime, timedelta


class PunishmentService:
    def __init__(self, plugin):
        self.plugin = plugin
        self.store = plugin.storage.open("punishments", {"mutes": {}})
        self.store.data.setdefault("mutes", {})

    @property
    def mutes(self) -> dict:
        return self.store.data["mutes"]

    def muteFor(self, key: str) -> dict | None:
        record = self.mutes.get(key)
        if record is None:
            return None

        until = record.get("until")
        if until is not None and float(until) <= time.time():
            self.mutes.pop(key, None)
            self.store.markDirty()
            return None

        return record

    def remainingMute(self, record: dict) -> float:
        until = record.get("until")
        if until is None:
            return math.inf
        return max(0.0, float(until) - time.time())

    def applyMute(self, key: str, name: str, seconds: float, reason: str, source: str) -> dict:
        record = {
            "name": name,
            "reason": reason or "No reason given",
            "source": source,
            "created": time.time(),
            "until": None if seconds == math.inf else time.time() + seconds,
        }
        self.mutes[key] = record
        self.store.markDirty()
        return record

    def liftMute(self, key: str) -> bool:
        if self.mutes.pop(key, None) is None:
            return False
        self.store.markDirty()
        return True

    def activeMutes(self) -> list:
        now = time.time()
        active = []
        for key in list(self.mutes.keys()):
            record = self.mutes[key]
            until = record.get("until")
            if until is not None and float(until) <= now:
                self.mutes.pop(key, None)
                self.store.markDirty()
                continue
            active.append((key, record))
        return active

    def applyBan(self, name: str, seconds: float, reason: str, source: str, uniqueId=None, xuid=None):
        expires = None if seconds == math.inf else datetime.now() + timedelta(seconds=seconds)
        return self.plugin.server.ban_list.add_ban(
            name,
            uniqueId,
            xuid,
            reason or "No reason given",
            expires,
            source,
        )

    def liftBan(self, name: str) -> bool:
        banList = self.plugin.server.ban_list
        if not banList.is_banned(name):
            return False
        banList.remove_ban(name)
        return True

    def isBanned(self, name: str) -> bool:
        return self.plugin.server.ban_list.is_banned(name)

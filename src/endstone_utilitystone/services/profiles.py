from __future__ import annotations

import time


class ProfileService:
    def __init__(self, plugin):
        self.plugin = plugin
        self.store = plugin.storage.open("profiles", {"players": {}, "names": {}})
        self.store.data.setdefault("players", {})
        self.store.data.setdefault("names", {})
        self._ignoreCache: dict = {}

    @property
    def players(self) -> dict:
        return self.store.data["players"]

    @property
    def names(self) -> dict:
        return self.store.data["names"]

    def profileFor(self, player) -> dict:
        return self.profileForKey(str(player.unique_id), player.name)

    def profileForKey(self, key: str, name: str = "") -> dict:
        profile = self.players.get(key)
        if profile is None:
            profile = {
                "name": name,
                "firstSeen": time.time(),
                "lastSeen": 0.0,
                "playtime": 0.0,
                "ignored": [],
            }
            self.players[key] = profile
            self.store.markDirty()
        return profile

    def recordJoin(self, player) -> dict:
        key = str(player.unique_id)
        profile = self.profileForKey(key, player.name)
        profile["name"] = player.name
        profile["lastSeen"] = time.time()
        self.names[player.name.lower()] = key
        self._ignoreCache[key] = set(profile.get("ignored", ()))
        self.store.markDirty()
        return profile

    def recordQuit(self, player, session) -> None:
        key = str(player.unique_id)
        profile = self.profileForKey(key, player.name)
        now = time.time()
        profile["lastSeen"] = now

        if session is not None:
            elapsed = now - session.lastPlaytimeSync
            if elapsed > 0.0:
                profile["playtime"] = float(profile.get("playtime", 0.0)) + elapsed

        self._ignoreCache.pop(key, None)
        self.store.markDirty()

    def syncPlaytime(self, players, sessions) -> None:
        now = time.time()
        changed = False

        for player in players:
            session = sessions.of(player)
            if session is None:
                continue

            elapsed = now - session.lastPlaytimeSync
            if elapsed <= 0.0:
                continue

            profile = self.profileForKey(session.key, session.name)
            profile["playtime"] = float(profile.get("playtime", 0.0)) + elapsed
            profile["lastSeen"] = now
            session.lastPlaytimeSync = now
            changed = True

        if changed:
            self.store.markDirty()

    def playtimeOf(self, key: str, session=None) -> float:
        profile = self.players.get(key)
        total = float(profile.get("playtime", 0.0)) if profile else 0.0
        if session is not None:
            total += max(0.0, time.time() - session.lastPlaytimeSync)
        return total

    def lookup(self, name: str):
        key = self.names.get(name.lower())
        if key is None:
            return None, None
        return key, self.players.get(key)

    def isIgnoring(self, ownerKey: str, targetKey: str) -> bool:
        cached = self._ignoreCache.get(ownerKey)
        if cached is None:
            return False
        return targetKey in cached

    def ignoredKeys(self, ownerKey: str) -> list:
        profile = self.players.get(ownerKey)
        if not profile:
            return []
        return list(profile.get("ignored", ()))

    def setIgnored(self, player, targetKey: str, ignored: bool) -> bool:
        key = str(player.unique_id)
        profile = self.profileForKey(key, player.name)
        current = profile.setdefault("ignored", [])

        if ignored:
            if targetKey in current:
                return False
            current.append(targetKey)
        else:
            if targetKey not in current:
                return False
            current.remove(targetKey)

        cached = self._ignoreCache.get(key)
        if cached is None:
            self._ignoreCache[key] = set(current)
        elif ignored:
            cached.add(targetKey)
        else:
            cached.discard(targetKey)

        self.store.markDirty()
        return True

    def displayName(self, key: str) -> str:
        profile = self.players.get(key)
        if not profile:
            return "unknown"
        return str(profile.get("name") or "unknown")

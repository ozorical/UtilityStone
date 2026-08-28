from __future__ import annotations

from endstone_utilitystone.util.locations import decodeLocation, encodeLocation

MAX_NAME_LENGTH = 24


def normalizeName(name: str) -> str:
    return name.strip().lower()


def isAcceptableName(name: str) -> bool:
    if not name or len(name) > MAX_NAME_LENGTH:
        return False
    return all(character.isalnum() or character in "-_" for character in name)


class HomeService:
    def __init__(self, plugin):
        self.plugin = plugin
        self.store = plugin.storage.open("homes", {})

    def homesOf(self, player) -> dict:
        return self.store.data.get(str(player.unique_id), {})

    def nameList(self, player) -> list:
        return sorted(self.homesOf(player).keys())

    def count(self, player) -> int:
        return len(self.homesOf(player))

    def limitFor(self, player):
        return self.plugin.settings.homeLimitFor(player)

    def setHome(self, player, name: str) -> str:
        key = normalizeName(name)
        if not isAcceptableName(key):
            return "invalid"

        owned = self.store.data.setdefault(str(player.unique_id), {})
        limit = self.limitFor(player)
        if limit is not None and key not in owned and len(owned) >= limit:
            return "limit"

        owned[key] = encodeLocation(player.location)
        self.store.markDirty()
        return "saved"

    def deleteHome(self, player, name: str) -> bool:
        owned = self.store.data.get(str(player.unique_id))
        if not owned:
            return False

        if owned.pop(normalizeName(name), None) is None:
            return False

        if not owned:
            self.store.data.pop(str(player.unique_id), None)

        self.store.markDirty()
        return True

    def resolve(self, player, name: str):
        payload = self.homesOf(player).get(normalizeName(name))
        if payload is None:
            return None
        return decodeLocation(self.plugin.server, payload)

    def onlyHomeName(self, player) -> str | None:
        owned = self.homesOf(player)
        if len(owned) != 1:
            return None
        return next(iter(owned))

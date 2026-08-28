from __future__ import annotations

from endstone_utilitystone.util.locations import decodeLocation, encodeLocation


class SpawnService:
    def __init__(self, plugin):
        self.plugin = plugin
        self.store = plugin.storage.open("spawn", {})

    def hasSpawn(self) -> bool:
        return "location" in self.store.data

    def setSpawn(self, location, creator: str) -> None:
        payload = encodeLocation(location)
        payload["createdBy"] = creator
        self.store.data["location"] = payload
        self.store.markDirty()

    def resolve(self):
        payload = self.store.data.get("location")
        if payload is None:
            return None
        return decodeLocation(self.plugin.server, payload)

    def markSeen(self, player) -> bool:
        seen = self.store.data.setdefault("seen", [])
        key = str(player.unique_id)
        if key in seen:
            return False
        seen.append(key)
        self.store.markDirty()
        return True

from __future__ import annotations

from endstone_utilitystone.services.homes import isAcceptableName, normalizeName
from endstone_utilitystone.util.locations import decodeLocation, encodeLocation


class WarpService:
    def __init__(self, plugin):
        self.plugin = plugin
        self.store = plugin.storage.open("warps", {})

    def nameList(self) -> list:
        return sorted(self.store.data.keys())

    def exists(self, name: str) -> bool:
        return normalizeName(name) in self.store.data

    def setWarp(self, name: str, location, creator: str) -> bool:
        key = normalizeName(name)
        if not isAcceptableName(key):
            return False

        payload = encodeLocation(location)
        payload["createdBy"] = creator
        self.store.data[key] = payload
        self.store.markDirty()
        return True

    def deleteWarp(self, name: str) -> bool:
        if self.store.data.pop(normalizeName(name), None) is None:
            return False
        self.store.markDirty()
        return True

    def resolve(self, name: str):
        payload = self.store.data.get(normalizeName(name))
        if payload is None:
            return None
        return decodeLocation(self.plugin.server, payload)

    def permissionFor(self, name: str) -> str:
        return f"utilitystone.warp.{normalizeName(name)}"

    def canUse(self, player, name: str) -> bool:
        if not self.plugin.settings.warpsNeedPermission:
            return True
        return player.has_permission(self.permissionFor(name))

    def visibleTo(self, player) -> list:
        if not self.plugin.settings.warpsNeedPermission:
            return self.nameList()
        return [name for name in self.nameList() if player.has_permission(self.permissionFor(name))]

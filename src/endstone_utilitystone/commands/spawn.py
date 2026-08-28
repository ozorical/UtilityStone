from __future__ import annotations

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.locations import describeLocation


class SpawnCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "spawn": self.goSpawn,
            "setspawn": self.createSpawn,
        }

    def goSpawn(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        destination = self.plugin.spawns.resolve()
        if destination is None:
            self.messages.failure(player, "A spawn point has not been set yet.")
            return True

        self.plugin.teleports.queueTeleport(player, destination, "spawn")
        return True

    def createSpawn(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        self.plugin.spawns.setSpawn(player.location, player.name)
        self.messages.success(player, f"Spawn point set to {describeLocation(player.location)}.")
        return True

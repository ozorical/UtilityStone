from __future__ import annotations

from endstone import ColorFormat

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.locations import describeLocation
from endstone_utilitystone.util.text import joinNames


class WarpCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "warp": self.useWarp,
            "setwarp": self.createWarp,
            "delwarp": self.deleteWarp,
            "warps": self.listWarps,
        }

    def useWarp(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        warps = self.plugin.warps
        if not args:
            return self.listWarps(player, args)

        name = args[0].lower()
        if not warps.exists(name):
            self.messages.failure(player, f"There is no warp called {name}.")
            return True

        if not warps.canUse(player, name):
            self.messages.failure(player, f"You do not have access to the warp {name}.")
            return True

        self.plugin.teleports.queueTeleport(player, warps.resolve(name), f"warp {name}")
        return True

    def createWarp(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        if not args:
            self.messages.failure(player, "Usage: /setwarp <name>")
            return True

        name = args[0].lower()
        if not self.plugin.warps.setWarp(name, player.location, player.name):
            self.messages.failure(player, "Warp names may only use letters, numbers, dashes and underscores.")
            return True

        self.messages.success(player, f"Warp {name} now points at {describeLocation(player.location)}.")
        return True

    def deleteWarp(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /delwarp <name>")
            return True

        name = args[0].lower()
        if not self.plugin.warps.deleteWarp(name):
            self.messages.failure(sender, f"There is no warp called {name}.")
            return True

        self.messages.success(sender, f"Deleted warp {name}.")
        return True

    def listWarps(self, sender, args: list) -> bool:
        names = self.plugin.warps.visibleTo(sender)

        if not names:
            self.messages.info(sender, "There are no warps available to you.")
            return True

        self.messages.heading(sender, f"Warps ({len(names)})")
        sender.send_message(f"{ColorFormat.WHITE}{joinNames(names)}")
        return True

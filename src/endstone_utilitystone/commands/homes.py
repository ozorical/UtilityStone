from __future__ import annotations

from endstone import ColorFormat

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.locations import describeLocation
from endstone_utilitystone.util.text import joinNames


class HomeCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "sethome": self.setHome,
            "home": self.goHome,
            "delhome": self.deleteHome,
            "homes": self.listHomes,
        }

    def setHome(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        name = args[0] if args else "home"
        homes = self.plugin.homes
        result = homes.setHome(player, name)

        if result == "invalid":
            self.messages.failure(player, "Home names may only use letters, numbers, dashes and underscores.")
            return True

        if result == "limit":
            limit = homes.limitFor(player)
            self.messages.failure(player, f"You have reached your limit of {limit} homes.")
            return True

        self.messages.success(player, f"Saved home {name.lower()} at {describeLocation(player.location)}.")
        return True

    def goHome(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        homes = self.plugin.homes
        if args:
            name = args[0].lower()
        else:
            name = homes.onlyHomeName(player) or "home"

        destination = homes.resolve(player, name)
        if destination is None:
            owned = homes.nameList(player)
            if owned:
                self.messages.failure(player, f"No home called {name}. You have: {joinNames(owned)}.")
            else:
                self.messages.failure(player, "You have not set a home yet. Use /sethome first.")
            return True

        self.plugin.teleports.queueTeleport(player, destination, f"your home {name}")
        return True

    def deleteHome(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        if not args:
            self.messages.failure(player, "Usage: /delhome <name>")
            return True

        name = args[0].lower()
        if not self.plugin.homes.deleteHome(player, name):
            self.messages.failure(player, f"You do not have a home called {name}.")
            return True

        self.messages.success(player, f"Deleted home {name}.")
        return True

    def listHomes(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        homes = self.plugin.homes
        owned = homes.nameList(player)
        if not owned:
            self.messages.info(player, "You have not set a home yet. Use /sethome to make one.")
            return True

        limit = homes.limitFor(player)
        allowance = "unlimited" if limit is None else str(limit)
        self.messages.heading(player, "Your homes")
        player.send_message(f"{ColorFormat.WHITE}{joinNames(owned)}")
        self.messages.listing(player, "Used", f"{len(owned)} of {allowance}")
        return True

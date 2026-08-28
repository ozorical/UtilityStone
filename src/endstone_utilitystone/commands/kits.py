from __future__ import annotations

from endstone import ColorFormat

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.durations import formatDuration
from endstone_utilitystone.util.text import joinNames


class KitCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "kit": self.claimKit,
            "kits": self.listKits,
        }

    def claimKit(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        if not args:
            return self.listKits(player, args)

        name = args[0].lower()
        definition = self.settings.kitDefinition(name)
        if definition is None:
            self.messages.failure(player, f"There is no kit called {name}.")
            return True

        kits = self.plugin.kits
        if not kits.canUse(player, name, definition):
            self.messages.failure(player, f"You do not have access to the {name} kit.")
            return True

        waiting = kits.cooldownRemaining(player, name, definition)
        if waiting > 0.0:
            self.messages.failure(player, f"You can claim the {name} kit again in {formatDuration(waiting)}.")
            return True

        granted, count, rejected = kits.grant(player, name, definition)
        if not granted:
            self.messages.failure(player, f"The {name} kit is not set up correctly. Tell an admin.")
            self.plugin.logger.warning(f"Kit '{name}' produced no valid items")
            return True

        kits.markUsed(player, name)
        self.messages.success(player, f"You claimed the {name} kit ({count} stacks).")

        if rejected:
            self.plugin.logger.warning(f"Kit '{name}' skipped {rejected} item entries that could not be built")

        return True

    def listKits(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        available = self.plugin.kits.availableTo(player)
        if not available:
            self.messages.info(player, "There are no kits available to you.")
            return True

        self.messages.heading(player, f"Kits ({len(available)})")
        player.send_message(f"{ColorFormat.WHITE}{joinNames(available)}")
        return True

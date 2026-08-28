from __future__ import annotations

from endstone_utilitystone.commands.base import CommandGroup

OTHERS_HEAL = "utilitystone.command.heal.others"
OTHERS_FEED = "utilitystone.command.feed.others"
OTHERS_FLY = "utilitystone.command.fly.others"
OTHERS_GOD = "utilitystone.command.god.others"
OTHERS_SPEED = "utilitystone.command.speed.others"


class StateCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "heal": self.healPlayer,
            "feed": self.feedPlayer,
            "fly": self.toggleFlight,
            "god": self.toggleGod,
            "speed": self.setSpeed,
            "repair": self.repairHeld,
        }

    def healPlayer(self, sender, args: list) -> bool:
        target = self.resolveSubject(sender, args, OTHERS_HEAL)
        if target is None:
            return True

        target.health = target.max_health
        self.messages.success(target, "You have been healed.")
        if not self.isSameSubject(sender, target):
            self.messages.success(sender, f"Healed {target.name}.")
        return True

    def feedPlayer(self, sender, args: list) -> bool:
        target = self.resolveSubject(sender, args, OTHERS_FEED)
        if target is None:
            return True

        console = self.server.command_sender
        self.server.dispatch_command(console, f'effect "{target.name}" saturation 1 255 true')
        self.messages.success(target, "Your hunger has been topped up.")
        if not self.isSameSubject(sender, target):
            self.messages.success(sender, f"Fed {target.name}.")
        return True

    def toggleFlight(self, sender, args: list) -> bool:
        target = self.resolveSubject(sender, args, OTHERS_FLY)
        if target is None:
            return True

        enabled = not target.allow_flight
        target.allow_flight = enabled
        if not enabled:
            target.is_flying = False

        state = "enabled" if enabled else "disabled"
        self.messages.success(target, f"Flight {state}.")
        if not self.isSameSubject(sender, target):
            self.messages.success(sender, f"Flight {state} for {target.name}.")
        return True

    def toggleGod(self, sender, args: list) -> bool:
        target = self.resolveSubject(sender, args, OTHERS_GOD)
        if target is None:
            return True

        protected = self.plugin.godPlayers
        if target.unique_id in protected:
            protected.discard(target.unique_id)
            state = "disabled"
        else:
            protected.add(target.unique_id)
            state = "enabled"

        self.messages.success(target, f"God mode {state}.")
        if not self.isSameSubject(sender, target):
            self.messages.success(sender, f"God mode {state} for {target.name}.")
        return True

    def setSpeed(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /speed <amount> [player]")
            return True

        try:
            amount = float(args[0])
        except ValueError:
            self.messages.failure(sender, "The speed has to be a number between 0.1 and 10.")
            return True

        if amount < 0.1 or amount > 10.0:
            self.messages.failure(sender, "The speed has to be between 0.1 and 10.")
            return True

        target = self.resolveSubject(sender, args, OTHERS_SPEED, 1)
        if target is None:
            return True

        scaled = amount / 10.0
        if target.is_flying or target.allow_flight:
            target.fly_speed = min(1.0, scaled)
            label = "Flight speed"
        else:
            target.walk_speed = min(1.0, scaled)
            label = "Walk speed"

        self.messages.success(target, f"{label} set to {amount:g}.")
        if not self.isSameSubject(sender, target):
            self.messages.success(sender, f"{label} set to {amount:g} for {target.name}.")
        return True

    def repairHeld(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        held = player.inventory.item_in_main_hand
        if held is None:
            self.messages.failure(player, "You are not holding anything.")
            return True

        meta = held.item_meta
        if not meta.has_damage:
            self.messages.failure(player, "That item does not need repairing.")
            return True

        meta.damage = 0
        held.set_item_meta(meta)
        player.inventory.item_in_main_hand = held
        self.messages.success(player, "Repaired the item in your hand.")
        return True

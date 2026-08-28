from __future__ import annotations

import math

from endstone import ColorFormat

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.durations import formatDuration, parseDuration


class ModerationCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "ban": self.banPlayer,
            "tempban": self.tempBanPlayer,
            "unban": self.unbanPlayer,
            "mute": self.mutePlayer,
            "unmute": self.unmutePlayer,
        }

    def banPlayer(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /ban <player> [reason]")
            return True

        reason = " ".join(args[1:]).strip() or "No reason given"
        return self._applyBan(sender, args[0], math.inf, reason)

    def tempBanPlayer(self, sender, args: list) -> bool:
        if len(args) < 2:
            self.messages.failure(sender, "Usage: /tempban <player> <duration> [reason]")
            return True

        seconds = parseDuration(args[1])
        if seconds is None:
            self.messages.failure(sender, "That duration is not valid. Try something like 30m, 2h or 7d.")
            return True

        reason = " ".join(args[2:]).strip() or "No reason given"
        return self._applyBan(sender, args[0], seconds, reason)

    def _applyBan(self, sender, token: str, seconds: float, reason: str) -> bool:
        source = self.senderName(sender)
        online = self.findPlayer(token, sender)
        name = online.name if online is not None else token.strip().strip('"')

        uniqueId = online.unique_id if online is not None else None
        xuid = online.xuid if online is not None else None

        self.plugin.punishments.applyBan(name, seconds, reason, source, uniqueId, xuid)

        window = formatDuration(seconds)
        if online is not None:
            online.kick(f"{ColorFormat.RED}You are banned.\n{ColorFormat.GRAY}Reason: {reason}\nLength: {window}")

        self.messages.success(sender, f"Banned {name} for {window}. Reason: {reason}")
        self.plugin.logger.info(f"{source} banned {name} for {window} ({reason})")
        return True

    def unbanPlayer(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /unban <player>")
            return True

        name = args[0].strip().strip('"')
        if not self.plugin.punishments.liftBan(name):
            self.messages.failure(sender, f"{name} is not banned.")
            return True

        self.messages.success(sender, f"Lifted the ban on {name}.")
        self.plugin.logger.info(f"{self.senderName(sender)} unbanned {name}")
        return True

    def mutePlayer(self, sender, args: list) -> bool:
        if len(args) < 2:
            self.messages.failure(sender, "Usage: /mute <player> <duration> [reason]")
            return True

        seconds = parseDuration(args[1])
        if seconds is None:
            self.messages.failure(sender, "That duration is not valid. Try 30m, 2h, 7d or perm.")
            return True

        target = self.requireTarget(sender, args[0])
        if target is None:
            return True

        reason = " ".join(args[2:]).strip() or "No reason given"
        source = self.senderName(sender)
        window = formatDuration(seconds)

        self.plugin.punishments.applyMute(str(target.unique_id), target.name, seconds, reason, source)

        self.messages.success(sender, f"Muted {target.name} for {window}. Reason: {reason}")
        self.messages.failure(target, f"You have been muted for {window}. Reason: {reason}")
        self.plugin.logger.info(f"{source} muted {target.name} for {window} ({reason})")
        return True

    def unmutePlayer(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /unmute <player>")
            return True

        profiles = self.plugin.profiles
        target = self.findPlayer(args[0], sender)
        if target is not None:
            targetKey = str(target.unique_id)
            targetName = target.name
        else:
            targetKey, profile = profiles.lookup(args[0])
            if targetKey is None:
                self.messages.failure(sender, f"Nobody called {args[0]} has played here.")
                return True
            targetName = str(profile.get("name", args[0])) if profile else args[0]

        if not self.plugin.punishments.liftMute(targetKey):
            self.messages.failure(sender, f"{targetName} is not muted.")
            return True

        self.messages.success(sender, f"Unmuted {targetName}.")
        if target is not None:
            self.messages.success(target, "You can chat again.")

        self.plugin.logger.info(f"{self.senderName(sender)} unmuted {targetName}")
        return True

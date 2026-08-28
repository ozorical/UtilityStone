from __future__ import annotations

from endstone import ColorFormat

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.durations import formatDuration
from endstone_utilitystone.util.text import joinNames


class TeleportCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "tpa": self.askToTeleport,
            "tpahere": self.askToSummon,
            "tpaccept": self.acceptRequest,
            "tpdeny": self.denyRequest,
            "tpcancel": self.cancelRequest,
            "back": self.goBack,
        }

    def askToTeleport(self, sender, args: list) -> bool:
        return self._sendRequest(sender, args, False)

    def askToSummon(self, sender, args: list) -> bool:
        return self._sendRequest(sender, args, True)

    def _sendRequest(self, sender, args: list, hereMode: bool) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        if not args:
            self.messages.failure(player, "Usage: /tpahere <player>" if hereMode else "Usage: /tpa <player>")
            return True

        target = self.requireTarget(player, args[0])
        if target is None:
            return True

        outcome = self.plugin.teleports.request(player, target, hereMode)
        if outcome == "self":
            self.messages.failure(player, "You cannot send a teleport request to yourself.")
            return True

        if outcome == "duplicate":
            self.messages.warn(player, f"{target.name} already has a pending request from you.")
            return True

        window = formatDuration(self.settings.teleportRequestSeconds)
        if hereMode:
            self.messages.success(player, f"Asked {target.name} to teleport to you. It expires in {window}.")
            self.messages.notice(target, f"{player.name} would like you to teleport to them.")
        else:
            self.messages.success(player, f"Teleport request sent to {target.name}. It expires in {window}.")
            self.messages.notice(target, f"{player.name} would like to teleport to you.")

        target.send_message(
            f"{ColorFormat.GRAY}Use {ColorFormat.WHITE}/tpaccept{ColorFormat.GRAY} or "
            f"{ColorFormat.WHITE}/tpdeny{ColorFormat.GRAY} to answer."
        )
        return True

    def acceptRequest(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        requester = self.findPlayer(args[0], player) if args else None
        if args and requester is None:
            self.messages.failure(player, f"No online player matches {args[0]}.")
            return True

        entry = self.plugin.teleports.takeRequest(player, requester)
        if entry is None:
            self.messages.failure(player, "You have no teleport requests waiting.")
            return True

        if entry.hereMode:
            self.plugin.teleports.queueTeleport(player, entry.requester.location, entry.requester.name)
            self.messages.notice(entry.requester, f"{player.name} accepted your request.")
        else:
            self.plugin.teleports.queueTeleport(entry.requester, player.location, player.name)
            self.messages.success(player, f"Accepted the request from {entry.requester.name}.")

        return True

    def denyRequest(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        requester = self.findPlayer(args[0], player) if args else None
        if args and requester is None:
            self.messages.failure(player, f"No online player matches {args[0]}.")
            return True

        entry = self.plugin.teleports.takeRequest(player, requester)
        if entry is None:
            self.messages.failure(player, "You have no teleport requests waiting.")
            return True

        self.messages.success(player, f"Turned down the request from {entry.requester.name}.")
        self.messages.warn(entry.requester, f"{player.name} turned down your teleport request.")
        return True

    def cancelRequest(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        entry = self.plugin.teleports.cancelOutgoing(player)
        if entry is None:
            self.messages.failure(player, "You do not have a teleport request out.")
            return True

        self.messages.success(player, f"Cancelled your request to {entry.target.name}.")
        self.messages.warn(entry.target, f"{player.name} cancelled their teleport request.")
        return True

    def goBack(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        destination = self.plugin.teleports.takeBack(player)
        if destination is None:
            self.messages.failure(player, "There is nowhere to go back to yet.")
            return True

        self.plugin.teleports.performTeleport(player, destination, "your previous location")
        return True

    def pendingSummary(self, player) -> str:
        entries = self.plugin.teleports.incomingFor(player)
        return joinNames(entry.requester.name for entry in entries)

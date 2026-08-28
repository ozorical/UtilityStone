from __future__ import annotations

from endstone import Player


class CommandGroup:
    def __init__(self, plugin):
        self.plugin = plugin
        self.server = plugin.server
        self.settings = plugin.settings
        self.messages = plugin.messages
        self.sessions = plugin.sessions

    def bindings(self) -> dict:
        return {}

    def asPlayer(self, sender):
        if isinstance(sender, Player):
            return sender
        self.messages.failure(sender, "Only a player in game can run that command.")
        return None

    def findPlayer(self, token: str, sender=None):
        if not token:
            return None

        name = token.strip().strip('"')
        if not name:
            return None

        if name.startswith("@"):
            if name.lower() == "@s" and isinstance(sender, Player):
                return sender
            return None

        found = self.server.get_player(name)
        if found is not None:
            return found

        lowered = name.lower()
        for player in self.server.online_players:
            if player.name.lower() == lowered:
                return player

        return None

    def requireTarget(self, sender, token: str):
        target = self.findPlayer(token, sender)
        if target is None:
            self.messages.failure(sender, f"No online player matches {token}.")
        return target

    def resolveSubject(self, sender, args: list, permission: str, index: int = 0):
        if len(args) > index and args[index].strip():
            if not sender.has_permission(permission):
                self.messages.failure(sender, "You cannot use that command on other players.")
                return None
            return self.requireTarget(sender, args[index])

        return self.asPlayer(sender)

    def isSameSubject(self, sender, target) -> bool:
        senderId = getattr(sender, "unique_id", None)
        return senderId is not None and senderId == target.unique_id

    def senderName(self, sender) -> str:
        return sender.name if sender is not None else "Console"

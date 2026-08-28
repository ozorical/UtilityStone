from __future__ import annotations

from endstone import ColorFormat, Player

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.text import joinNames, stripColors


class MessagingCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "pm": self.sendPrivate,
            "reply": self.replyPrivate,
            "ignore": self.startIgnoring,
            "unignore": self.stopIgnoring,
            "ignorelist": self.showIgnored,
            "broadcast": self.broadcastMessage,
        }

    def sendPrivate(self, sender, args: list) -> bool:
        if len(args) < 2:
            self.messages.failure(sender, "Usage: /pm <player> <message>")
            return True

        target = self.requireTarget(sender, args[0])
        if target is None:
            return True

        body = " ".join(args[1:]).strip()
        if not body:
            self.messages.failure(sender, "You need something to say.")
            return True

        return self.deliver(sender, target, body)

    def replyPrivate(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        if not args:
            self.messages.failure(player, "Usage: /reply <message>")
            return True

        session = self.sessions.of(player)
        if session is None or session.replyTarget is None:
            self.messages.failure(player, "There is nobody to reply to.")
            return True

        target = self.server.get_player(session.replyTarget)
        if target is None:
            self.messages.failure(player, "That player is no longer online.")
            return True

        return self.deliver(player, target, " ".join(args).strip())

    def deliver(self, sender, target, body: str) -> bool:
        senderName = self.senderName(sender)
        senderKey = str(sender.unique_id) if isinstance(sender, Player) else None

        if senderKey is not None and self.plugin.profiles.isIgnoring(str(target.unique_id), senderKey):
            self.messages.failure(sender, f"{target.name} is not accepting messages from you.")
            return True

        clean = stripColors(body)
        sender.send_message(f"{ColorFormat.LIGHT_PURPLE}to {target.name}: {ColorFormat.WHITE}{clean}")
        target.send_message(f"{ColorFormat.LIGHT_PURPLE}from {senderName}: {ColorFormat.WHITE}{clean}")

        targetSession = self.sessions.of(target)
        if targetSession is not None:
            targetSession.replyTarget = senderName

        if isinstance(sender, Player):
            senderSession = self.sessions.of(sender)
            if senderSession is not None:
                senderSession.replyTarget = target.name
            self.plugin.afk.touch(sender, senderSession)

        if targetSession is not None and targetSession.isAfk:
            reason = f" ({targetSession.afkReason})" if targetSession.afkReason else ""
            self.messages.warn(sender, f"{target.name} is currently AFK{reason}.")

        return True

    def startIgnoring(self, sender, args: list) -> bool:
        return self._changeIgnore(sender, args, True)

    def stopIgnoring(self, sender, args: list) -> bool:
        return self._changeIgnore(sender, args, False)

    def _changeIgnore(self, sender, args: list, ignoring: bool) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        verb = "ignore" if ignoring else "unignore"
        if not args:
            self.messages.failure(player, f"Usage: /{verb} <player>")
            return True

        profiles = self.plugin.profiles
        target = self.findPlayer(args[0], player)
        if target is not None:
            targetKey = str(target.unique_id)
            targetName = target.name
        else:
            targetKey, profile = profiles.lookup(args[0])
            if targetKey is None:
                self.messages.failure(player, f"Nobody called {args[0]} has played here.")
                return True
            targetName = str(profile.get("name", args[0])) if profile else args[0]

        if targetKey == str(player.unique_id):
            self.messages.failure(player, "You cannot ignore yourself.")
            return True

        if not profiles.setIgnored(player, targetKey, ignoring):
            state = "already" if ignoring else "not"
            self.messages.warn(player, f"You are {state} ignoring {targetName}.")
            return True

        state = "now ignoring" if ignoring else "no longer ignoring"
        self.messages.success(player, f"You are {state} {targetName}.")
        return True

    def showIgnored(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        profiles = self.plugin.profiles
        keys = profiles.ignoredKeys(str(player.unique_id))
        if not keys:
            self.messages.info(player, "You are not ignoring anybody.")
            return True

        names = [profiles.displayName(key) for key in keys]
        self.messages.heading(player, f"Ignored players ({len(names)})")
        player.send_message(f"{ColorFormat.WHITE}{joinNames(names)}")
        return True

    def broadcastMessage(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /broadcast <message>")
            return True

        body = " ".join(args).strip()
        header = f"{ColorFormat.GOLD}{ColorFormat.BOLD}Broadcast{ColorFormat.RESET} "
        self.server.broadcast_message(f"{header}{ColorFormat.YELLOW}{body}")
        return True

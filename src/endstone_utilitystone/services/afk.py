from __future__ import annotations

import time

from endstone import ColorFormat

from endstone_utilitystone.util.text import colorize, stripColors


class AfkService:
    def __init__(self, plugin):
        self.plugin = plugin

    def markAfk(self, player, session, reason: str = "", announce: bool = True) -> None:
        if session.isAfk:
            return

        session.isAfk = True
        session.afkSince = time.time()
        session.afkReason = stripColors(reason.strip())[:64]

        if announce and self.plugin.settings.afkAnnounce:
            suffix = f" ({session.afkReason})" if session.afkReason else ""
            self.broadcast(f"{ColorFormat.GRAY}{player.name} is now AFK{suffix}.")

    def clearAfk(self, player, session, announce: bool = True) -> None:
        if not session.isAfk:
            return

        session.isAfk = False
        session.afkSince = 0.0
        session.afkReason = ""
        session.touch()

        if announce and self.plugin.settings.afkAnnounce:
            self.broadcast(f"{ColorFormat.GRAY}{player.name} is no longer AFK.")

    def toggle(self, player, reason: str = "") -> bool:
        session = self.plugin.sessions.of(player)
        if session is None:
            return False

        if session.isAfk:
            self.clearAfk(player, session)
            return False

        self.markAfk(player, session, reason)
        return True

    def touch(self, player, session=None) -> None:
        active = session if session is not None else self.plugin.sessions.of(player)
        if active is None:
            return

        active.touch()
        if active.isAfk:
            self.clearAfk(player, active)

    def tag(self, session) -> str:
        if session is None or not session.isAfk:
            return ""
        return colorize(self.plugin.settings.chatAfkTag)

    def broadcast(self, message: str) -> None:
        server = self.plugin.server
        server.broadcast_message(message)

    def sample(self) -> None:
        settings = self.plugin.settings
        if not settings.afkEnabled:
            return

        sessions = self.plugin.sessions
        now = time.time()
        timeout = settings.afkTimeoutSeconds

        for player in self.plugin.server.online_players:
            session = sessions.of(player)
            if session is None:
                continue

            location = player.location
            sample = (round(location.x, 1), round(location.y, 1), round(location.z, 1))

            if session.lastSample != sample:
                session.lastSample = sample
                session.lastActivity = now
                if session.isAfk:
                    self.clearAfk(player, session)
                continue

            if not session.isAfk and (now - session.lastActivity) >= timeout:
                self.markAfk(player, session)

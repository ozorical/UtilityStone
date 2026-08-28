from __future__ import annotations

import time

from endstone import ColorFormat

from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.util.durations import formatDuration, formatTimestamp
from endstone_utilitystone.util.locations import describeLocation

OTHERS_PING = "utilitystone.command.ping.others"
OTHERS_PLAYTIME = "utilitystone.command.playtime.others"


class InfoCommands(CommandGroup):
    def bindings(self) -> dict:
        return {
            "who": self.listOnline,
            "ping": self.showPing,
            "playtime": self.showPlaytime,
            "seen": self.showSeen,
            "whois": self.showWhois,
            "afk": self.toggleAfk,
            "utilitystone": self.pluginControl,
        }

    def listOnline(self, sender, args: list) -> bool:
        players = self.server.online_players
        if not players:
            self.messages.info(sender, "Nobody is online right now.")
            return True

        entries = []
        for player in sorted(players, key=lambda item: item.name.lower()):
            session = self.sessions.of(player)
            marker = f"{ColorFormat.GRAY} [AFK]" if session is not None and session.isAfk else ""
            entries.append(f"{ColorFormat.WHITE}{player.name}{marker}")

        self.messages.heading(sender, f"Online ({len(players)} of {self.server.max_players})")
        sender.send_message(f"{ColorFormat.GRAY}, ".join(entries))
        return True

    def showPing(self, sender, args: list) -> bool:
        target = self.resolveSubject(sender, args, OTHERS_PING)
        if target is None:
            return True

        latency = target.ping
        if latency < 80:
            colour = ColorFormat.GREEN
        elif latency < 200:
            colour = ColorFormat.YELLOW
        else:
            colour = ColorFormat.RED

        subject = "Your ping is" if self.isSameSubject(sender, target) else f"{target.name} has a ping of"
        self.messages.info(sender, f"{subject} {colour}{latency}ms{ColorFormat.GRAY}.")
        return True

    def showPlaytime(self, sender, args: list) -> bool:
        target = self.resolveSubject(sender, args, OTHERS_PLAYTIME)
        if target is None:
            return True

        session = self.sessions.of(target)
        total = self.plugin.profiles.playtimeOf(str(target.unique_id), session)
        subject = "You have played for" if self.isSameSubject(sender, target) else f"{target.name} has played for"
        self.messages.info(sender, f"{subject} {formatDuration(total, 3)}.")
        return True

    def showSeen(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /seen <player>")
            return True

        online = self.findPlayer(args[0], sender)
        if online is not None:
            session = self.sessions.of(online)
            connected = formatDuration(time.time() - session.joinedAt) if session else "a moment"
            self.messages.info(sender, f"{online.name} is online and has been for {connected}.")
            return True

        key, profile = self.plugin.profiles.lookup(args[0])
        if key is None or profile is None:
            self.messages.failure(sender, f"Nobody called {args[0]} has played here.")
            return True

        lastSeen = float(profile.get("lastSeen", 0.0))
        away = formatDuration(time.time() - lastSeen) if lastSeen else "unknown"
        self.messages.heading(sender, str(profile.get("name", args[0])))
        self.messages.listing(sender, "Last seen", f"{formatTimestamp(lastSeen)} ({away} ago)")
        self.messages.listing(sender, "Playtime", formatDuration(float(profile.get("playtime", 0.0)), 3))
        self.messages.listing(sender, "First joined", formatTimestamp(float(profile.get("firstSeen", 0.0))))
        return True

    def showWhois(self, sender, args: list) -> bool:
        if not args:
            self.messages.failure(sender, "Usage: /whois <player>")
            return True

        target = self.requireTarget(sender, args[0])
        if target is None:
            return True

        session = self.sessions.of(target)
        profiles = self.plugin.profiles
        mute = self.plugin.punishments.muteFor(str(target.unique_id))

        self.messages.heading(sender, target.name)
        self.messages.listing(sender, "Unique id", str(target.unique_id))
        self.messages.listing(sender, "Ping", f"{target.ping}ms")
        self.messages.listing(sender, "Game mode", target.game_mode.name.title())
        self.messages.listing(sender, "Health", f"{target.health} of {target.max_health}")
        self.messages.listing(sender, "Location", describeLocation(target.location))
        self.messages.listing(sender, "Device", f"{target.device_os} on {target.game_version}")
        self.messages.listing(
            sender, "Playtime", formatDuration(profiles.playtimeOf(str(target.unique_id), session), 3)
        )

        if session is not None and session.isAfk:
            reason = f" ({session.afkReason})" if session.afkReason else ""
            self.messages.listing(sender, "Status", f"AFK for {formatDuration(time.time() - session.afkSince)}{reason}")

        if mute is not None:
            remaining = self.plugin.punishments.remainingMute(mute)
            self.messages.listing(sender, "Muted", f"{formatDuration(remaining)} left ({mute.get('reason')})")

        return True

    def toggleAfk(self, sender, args: list) -> bool:
        player = self.asPlayer(sender)
        if player is None:
            return True

        reason = " ".join(args).strip()
        if self.plugin.afk.toggle(player, reason):
            self.messages.info(player, "You are now marked as AFK.")
        else:
            self.messages.info(player, "You are no longer marked as AFK.")
        return True

    def pluginControl(self, sender, args: list) -> bool:
        action = args[0].lower() if args else "info"

        if action == "reload":
            self.plugin.reloadSettings()
            self.messages.success(sender, "Configuration reloaded.")
            return True

        teleports = self.plugin.teleports

        self.messages.heading(sender, f"UtilityStone {self.plugin.pluginVersion}")
        self.messages.listing(sender, "Author", "Ozz")
        self.messages.listing(sender, "Commands", str(self.plugin.router.count))
        self.messages.listing(sender, "Tracked players", str(self.sessions.count))
        self.messages.listing(sender, "Pending teleports", str(teleports.pendingCount))
        self.messages.listing(sender, "Open requests", str(teleports.requestCount))
        self.messages.listing(sender, "Server tick", f"{self.server.average_tps:.2f} tps")

        discord = self.plugin.discord
        if discord is not None:
            state = "connected" if discord.connected else discord.state
            self.messages.listing(sender, "Discord relay", state)

        return True

from __future__ import annotations

import time

from endstone_utilitystone.util.durations import formatDuration
from endstone_utilitystone.util.locations import decodeLocation, encodeLocation, flatDistanceSquared

INSTANT_PERMISSION = "utilitystone.teleport.instant"
NO_COOLDOWN_PERMISSION = "utilitystone.teleport.nocooldown"


class TeleportRequest:
    __slots__ = ("requester", "target", "hereMode", "expiresAt")

    def __init__(self, requester, target, hereMode: bool, expiresAt: float):
        self.requester = requester
        self.target = target
        self.hereMode = hereMode
        self.expiresAt = expiresAt


class PendingTeleport:
    __slots__ = ("player", "destination", "origin", "readyAt", "label")

    def __init__(self, player, destination, origin, readyAt: float, label: str):
        self.player = player
        self.destination = destination
        self.origin = origin
        self.readyAt = readyAt
        self.label = label


class TeleportService:
    def __init__(self, plugin):
        self.plugin = plugin
        self._incoming: dict = {}
        self._outgoing: dict = {}
        self._pending: dict = {}

    @property
    def pendingCount(self) -> int:
        return len(self._pending)

    @property
    def requestCount(self) -> int:
        return sum(len(entries) for entries in self._incoming.values())

    def request(self, requester, target, hereMode: bool) -> str:
        if requester.unique_id == target.unique_id:
            return "self"

        now = time.time()
        entries = self._incoming.setdefault(target.unique_id, {})
        existing = entries.get(requester.unique_id)
        if existing is not None and existing.expiresAt > now:
            return "duplicate"

        previousTarget = self._outgoing.get(requester.unique_id)
        if previousTarget is not None and previousTarget != target.unique_id:
            older = self._incoming.get(previousTarget)
            if older is not None:
                older.pop(requester.unique_id, None)

        entries[requester.unique_id] = TeleportRequest(
            requester, target, hereMode, now + self.plugin.settings.teleportRequestSeconds
        )
        self._outgoing[requester.unique_id] = target.unique_id
        return "sent"

    def incomingFor(self, target) -> list:
        entries = self._incoming.get(target.unique_id)
        if not entries:
            return []

        now = time.time()
        return [entry for entry in entries.values() if entry.expiresAt > now]

    def takeRequest(self, target, requester=None):
        entries = self._incoming.get(target.unique_id)
        if not entries:
            return None

        now = time.time()
        found = None

        if requester is not None:
            candidate = entries.pop(requester.unique_id, None)
            if candidate is not None and candidate.expiresAt > now:
                found = candidate
        else:
            for key in list(entries.keys()):
                candidate = entries.pop(key)
                if candidate.expiresAt > now:
                    found = candidate
                    break

        if not entries:
            self._incoming.pop(target.unique_id, None)

        if found is not None:
            self._outgoing.pop(found.requester.unique_id, None)

        return found

    def cancelOutgoing(self, requester):
        targetKey = self._outgoing.pop(requester.unique_id, None)
        if targetKey is None:
            return None

        entries = self._incoming.get(targetKey)
        if not entries:
            return None

        found = entries.pop(requester.unique_id, None)
        if not entries:
            self._incoming.pop(targetKey, None)
        return found

    def forget(self, player) -> None:
        key = player.unique_id
        self._pending.pop(key, None)

        entries = self._incoming.pop(key, None)
        if entries:
            for requesterKey in entries:
                self._outgoing.pop(requesterKey, None)

        targetKey = self._outgoing.pop(key, None)
        if targetKey is not None:
            waiting = self._incoming.get(targetKey)
            if waiting is not None:
                waiting.pop(key, None)
                if not waiting:
                    self._incoming.pop(targetKey, None)

    def queueTeleport(self, player, destination, label: str, chargeCooldown: bool = True) -> bool:
        messages = self.plugin.messages
        if destination is None:
            messages.failure(player, "That destination is not available right now.")
            return False

        settings = self.plugin.settings
        session = self.plugin.sessions.of(player)
        now = time.time()
        skipCooldown = player.has_permission(NO_COOLDOWN_PERMISSION)

        if session is not None and chargeCooldown and not skipCooldown:
            waiting = session.cooldownRemaining("teleport", now)
            if waiting > 0.0:
                messages.failure(player, f"You can teleport again in {formatDuration(waiting)}.")
                return False

        warmup = 0.0 if player.has_permission(INSTANT_PERMISSION) else settings.teleportWarmupSeconds
        if warmup <= 0.0:
            return self.performTeleport(player, destination, label, chargeCooldown)

        self._pending[player.unique_id] = PendingTeleport(
            player, destination, player.location, now + warmup, label
        )
        messages.notice(player, f"Teleporting to {label} in {formatDuration(warmup)}. Stand still.")
        return True

    def performTeleport(self, player, destination, label: str, chargeCooldown: bool = True) -> bool:
        settings = self.plugin.settings
        messages = self.plugin.messages
        session = self.plugin.sessions.of(player)

        if session is not None:
            session.pushBack(encodeLocation(player.location), settings.backHistorySize)

        if not player.teleport(destination):
            messages.failure(player, "The server refused that teleport.")
            return False

        if session is not None and chargeCooldown and not player.has_permission(NO_COOLDOWN_PERMISSION):
            session.startCooldown("teleport", settings.teleportCooldownSeconds, time.time())

        messages.success(player, f"Teleported to {label}.")
        return True

    def rememberLocation(self, player, location=None) -> None:
        session = self.plugin.sessions.of(player)
        if session is None:
            return

        source = location if location is not None else player.location
        session.pushBack(encodeLocation(source), self.plugin.settings.backHistorySize)

    def takeBack(self, player):
        session = self.plugin.sessions.of(player)
        if session is None:
            return None

        payload = session.popBack()
        if payload is None:
            return None
        return decodeLocation(self.plugin.server, payload)

    def tick(self) -> None:
        if not self._incoming and not self._pending:
            return

        now = time.time()
        if self._incoming:
            self._expireRequests(now)
        if self._pending:
            self._advancePending(now)

    def _expireRequests(self, now: float) -> None:
        for targetKey in list(self._incoming.keys()):
            entries = self._incoming.get(targetKey)
            if not entries:
                self._incoming.pop(targetKey, None)
                continue

            for requesterKey in list(entries.keys()):
                entry = entries[requesterKey]
                if entry.expiresAt > now:
                    continue

                entries.pop(requesterKey, None)
                self._outgoing.pop(requesterKey, None)
                self._notifyExpired(entry)

            if not entries:
                self._incoming.pop(targetKey, None)

    def _notifyExpired(self, entry: TeleportRequest) -> None:
        try:
            self.plugin.messages.warn(
                entry.requester, f"Your teleport request to {entry.target.name} expired."
            )
        except Exception:
            pass

    def _advancePending(self, now: float) -> None:
        settings = self.plugin.settings
        messages = self.plugin.messages
        tolerance = settings.teleportMoveTolerance * settings.teleportMoveTolerance

        for key in list(self._pending.keys()):
            pending = self._pending.get(key)
            if pending is None:
                continue

            player = pending.player
            try:
                usable = player.is_valid and not player.is_dead
            except Exception:
                usable = False

            if not usable:
                self._pending.pop(key, None)
                continue

            if settings.teleportCancelOnMove:
                if flatDistanceSquared(player.location, pending.origin) > tolerance:
                    self._pending.pop(key, None)
                    messages.failure(player, "Teleport cancelled because you moved.")
                    continue

            if now < pending.readyAt:
                continue

            self._pending.pop(key, None)
            self.performTeleport(player, pending.destination, pending.label)

    def clear(self) -> None:
        self._incoming.clear()
        self._outgoing.clear()
        self._pending.clear()

from __future__ import annotations

from endstone_utilitystone.util.durations import parseDuration


def plainValue(value):
    unwrap = getattr(value, "unwrap", None)
    if callable(unwrap):
        try:
            value = unwrap()
        except Exception:
            pass

    if isinstance(value, dict):
        return {str(key): plainValue(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plainValue(item) for item in value]
    return value


def sectionOf(source, name: str) -> dict:
    value = source.get(name) if isinstance(source, dict) else None
    return value if isinstance(value, dict) else {}


def readBool(source: dict, key: str, fallback: bool) -> bool:
    value = source.get(key, fallback)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def readInt(source: dict, key: str, fallback: int, lowest: int, highest: int) -> int:
    try:
        value = int(source.get(key, fallback))
    except (TypeError, ValueError):
        value = fallback
    return max(lowest, min(highest, value))


def readFloat(source: dict, key: str, fallback: float, lowest: float, highest: float) -> float:
    try:
        value = float(source.get(key, fallback))
    except (TypeError, ValueError):
        value = fallback
    return max(lowest, min(highest, value))


def readText(source: dict, key: str, fallback: str) -> str:
    value = source.get(key, fallback)
    return str(value) if value is not None else fallback


class Settings:
    def __init__(self, raw=None):
        self.applyFrom(raw)

    def applyFrom(self, raw) -> None:
        data = plainValue(raw)
        if not isinstance(data, dict):
            data = {}

        storage = sectionOf(data, "storage")
        self.saveIntervalSeconds = readFloat(storage, "saveIntervalSeconds", 30.0, 5.0, 900.0)
        self.playtimeSyncSeconds = readFloat(storage, "playtimeSyncSeconds", 120.0, 15.0, 1800.0)

        messages = sectionOf(data, "messages")
        self.prefix = readText(messages, "prefix", "&8[&bUtilityStone&8]&r ")
        self.usePrefix = readBool(messages, "usePrefix", True)

        homes = sectionOf(data, "homes")
        self.homeDefaultLimit = readInt(homes, "defaultLimit", 3, 0, 500)
        self.homeLimits = {}
        for node, limit in sectionOf(homes, "limits").items():
            try:
                self.homeLimits[str(node)] = max(0, min(500, int(limit)))
            except (TypeError, ValueError):
                continue

        warps = sectionOf(data, "warps")
        self.warpsNeedPermission = readBool(warps, "requirePerWarpPermission", False)

        spawn = sectionOf(data, "spawn")
        self.spawnOnFirstJoin = readBool(spawn, "teleportOnFirstJoin", False)

        teleport = sectionOf(data, "teleport")
        self.teleportWarmupSeconds = readFloat(teleport, "warmupSeconds", 3.0, 0.0, 60.0)
        self.teleportCooldownSeconds = readFloat(teleport, "cooldownSeconds", 5.0, 0.0, 3600.0)
        self.teleportRequestSeconds = readFloat(teleport, "requestTimeoutSeconds", 60.0, 10.0, 600.0)
        self.teleportCancelOnMove = readBool(teleport, "cancelOnMove", True)
        self.teleportMoveTolerance = readFloat(teleport, "moveTolerance", 0.75, 0.1, 16.0)
        self.teleportPollTicks = readInt(teleport, "pollTicks", 10, 2, 40)
        self.backOnDeath = readBool(teleport, "rememberDeathLocation", True)
        self.backHistorySize = readInt(teleport, "historySize", 5, 1, 25)

        chat = sectionOf(data, "chat")
        self.chatManaged = readBool(chat, "manageFormat", True)
        self.chatFormat = readText(chat, "format", "<{name}> {message}")
        self.chatAfkTag = readText(chat, "afkTag", "&7[AFK] &r")

        afk = sectionOf(data, "afk")
        self.afkEnabled = readBool(afk, "enabled", True)
        self.afkTimeoutSeconds = readFloat(afk, "timeoutSeconds", 300.0, 30.0, 7200.0)
        self.afkSampleSeconds = readFloat(afk, "sampleSeconds", 5.0, 1.0, 60.0)
        self.afkAnnounce = readBool(afk, "announce", True)

        discord = sectionOf(data, "discord")
        self.discordEnabled = readBool(discord, "enabled", True)
        self.discordRelayChat = readBool(discord, "relayChat", True)
        self.discordRelayDeaths = readBool(discord, "relayDeaths", True)
        self.discordRelayJoinLeave = readBool(discord, "relayJoinLeave", True)
        self.discordRelayServerState = readBool(discord, "relayServerState", True)
        self.discordSendIntervalSeconds = readFloat(discord, "sendIntervalSeconds", 1.5, 0.5, 30.0)
        self.discordPollTicks = readInt(discord, "inboundPollTicks", 10, 2, 40)
        self.discordInboundLimit = readInt(discord, "maxInboundLength", 256, 32, 1024)
        self.discordChatFormat = readText(discord, "chatFormat", "**{name}**: {message}")
        self.discordEventFormat = readText(discord, "eventFormat", "_{message}_")
        self.discordInboundFormat = readText(
            discord, "inboundFormat", "&9[Discord] &b{name}&7: &f{message}"
        )

        connection = sectionOf(data, "connection")
        self.joinMessage = readText(connection, "joinMessage", "")
        self.quitMessage = readText(connection, "quitMessage", "")
        self.welcomeMessage = readText(connection, "welcomeMessage", "")

        self.kits = sectionOf(data, "kits")

    def kitDefinition(self, name: str) -> dict | None:
        definition = self.kits.get(name.lower())
        return definition if isinstance(definition, dict) else None

    def kitNames(self) -> list[str]:
        return sorted(key for key, value in self.kits.items() if isinstance(value, dict))

    def kitCooldownSeconds(self, definition: dict) -> float:
        parsed = parseDuration(definition.get("cooldown"))
        return 0.0 if parsed is None else parsed

    def homeLimitFor(self, player) -> int | None:
        if player.has_permission("utilitystone.homes.unlimited"):
            return None

        limit = self.homeDefaultLimit
        for node, value in self.homeLimits.items():
            if value > limit and player.has_permission(node):
                limit = value
        return limit

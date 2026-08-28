from __future__ import annotations

from pathlib import Path

from endstone.plugin import Plugin

from endstone_utilitystone.commands import COMMAND_GROUPS
from endstone_utilitystone.core.messages import Messages
from endstone_utilitystone.core.router import CommandRouter
from endstone_utilitystone.core.sessions import SessionRegistry
from endstone_utilitystone.core.settings import Settings
from endstone_utilitystone.core.storage import StorageManager
from endstone_utilitystone.integrations.discord import DiscordBridge
from endstone_utilitystone.listeners import LISTENERS
from endstone_utilitystone.services.afk import AfkService
from endstone_utilitystone.services.homes import HomeService
from endstone_utilitystone.services.kits import KitService
from endstone_utilitystone.services.profiles import ProfileService
from endstone_utilitystone.services.punishments import PunishmentService
from endstone_utilitystone.services.spawns import SpawnService
from endstone_utilitystone.services.teleports import TeleportService
from endstone_utilitystone.services.warps import WarpService


class UtilityStone(Plugin):
    api_version = "0.11"
    load = "POSTWORLD"
    prefix = "UtilityStone"
    authors = ["Ozz"]

    commands = {
        "sethome": {
            "description": "Save your current position as a home.",
            "usages": ["/sethome [name: str]"],
            "permissions": ["utilitystone.command.sethome"],
        },
        "home": {
            "description": "Travel to one of your homes.",
            "usages": ["/home [name: str]"],
            "permissions": ["utilitystone.command.home"],
        },
        "delhome": {
            "description": "Remove one of your homes.",
            "usages": ["/delhome <name: str>"],
            "permissions": ["utilitystone.command.delhome"],
        },
        "homes": {
            "description": "List the homes you have saved.",
            "usages": ["/homes"],
            "permissions": ["utilitystone.command.homes"],
        },
        "warp": {
            "description": "Travel to a server warp.",
            "usages": ["/warp [name: str]"],
            "permissions": ["utilitystone.command.warp"],
        },
        "warps": {
            "description": "List the warps you can use.",
            "usages": ["/warps"],
            "permissions": ["utilitystone.command.warps"],
        },
        "setwarp": {
            "description": "Create or move a server warp.",
            "usages": ["/setwarp <name: str>"],
            "permissions": ["utilitystone.command.setwarp"],
        },
        "delwarp": {
            "description": "Delete a server warp.",
            "usages": ["/delwarp <name: str>"],
            "permissions": ["utilitystone.command.delwarp"],
        },
        "spawn": {
            "description": "Travel to the server spawn point.",
            "usages": ["/spawn"],
            "permissions": ["utilitystone.command.spawn"],
        },
        "setspawn": {
            "description": "Set the server spawn point to your position.",
            "usages": ["/setspawn"],
            "permissions": ["utilitystone.command.setspawn"],
        },
        "tpa": {
            "description": "Ask another player if you may teleport to them.",
            "usages": ["/tpa <player: target>"],
            "permissions": ["utilitystone.command.tpa"],
        },
        "tpahere": {
            "description": "Ask another player to teleport to you.",
            "usages": ["/tpahere <player: target>"],
            "permissions": ["utilitystone.command.tpahere"],
        },
        "tpaccept": {
            "description": "Accept a teleport request.",
            "usages": ["/tpaccept [player: target]"],
            "aliases": ["tpyes"],
            "permissions": ["utilitystone.command.tpaccept"],
        },
        "tpdeny": {
            "description": "Turn down a teleport request.",
            "usages": ["/tpdeny [player: target]"],
            "aliases": ["tpno"],
            "permissions": ["utilitystone.command.tpdeny"],
        },
        "tpcancel": {
            "description": "Cancel the teleport request you sent.",
            "usages": ["/tpcancel"],
            "permissions": ["utilitystone.command.tpcancel"],
        },
        "back": {
            "description": "Return to where you last teleported from.",
            "usages": ["/back"],
            "permissions": ["utilitystone.command.back"],
        },
        "heal": {
            "description": "Restore health.",
            "usages": ["/heal [player: target]"],
            "permissions": ["utilitystone.command.heal"],
        },
        "feed": {
            "description": "Restore hunger.",
            "usages": ["/feed [player: target]"],
            "permissions": ["utilitystone.command.feed"],
        },
        "fly": {
            "description": "Toggle the ability to fly.",
            "usages": ["/fly [player: target]"],
            "permissions": ["utilitystone.command.fly"],
        },
        "god": {
            "description": "Toggle damage immunity.",
            "usages": ["/god [player: target]"],
            "permissions": ["utilitystone.command.god"],
        },
        "speed": {
            "description": "Change walk or flight speed.",
            "usages": ["/speed <amount: float> [player: target]"],
            "permissions": ["utilitystone.command.speed"],
        },
        "repair": {
            "description": "Repair the item you are holding.",
            "usages": ["/repair"],
            "permissions": ["utilitystone.command.repair"],
        },
        "pm": {
            "description": "Send a private message.",
            "usages": ["/pm <player: target> <message: message>"],
            "aliases": ["dm"],
            "permissions": ["utilitystone.command.pm"],
        },
        "reply": {
            "description": "Reply to the last private message you received.",
            "usages": ["/reply <message: message>"],
            "aliases": ["r"],
            "permissions": ["utilitystone.command.reply"],
        },
        "ignore": {
            "description": "Stop seeing messages from a player.",
            "usages": ["/ignore <player: str>"],
            "permissions": ["utilitystone.command.ignore"],
        },
        "unignore": {
            "description": "Start seeing messages from a player again.",
            "usages": ["/unignore <player: str>"],
            "permissions": ["utilitystone.command.unignore"],
        },
        "ignorelist": {
            "description": "List the players you are ignoring.",
            "usages": ["/ignorelist"],
            "permissions": ["utilitystone.command.ignorelist"],
        },
        "broadcast": {
            "description": "Send a highlighted message to everyone.",
            "usages": ["/broadcast <message: message>"],
            "permissions": ["utilitystone.command.broadcast"],
        },
        "ban": {
            "description": "Ban a player permanently.",
            "usages": ["/ban <player: str> [reason: message]"],
            "permissions": ["utilitystone.command.ban"],
        },
        "tempban": {
            "description": "Ban a player for a set length of time.",
            "usages": ["/tempban <player: str> <duration: str> [reason: message]"],
            "permissions": ["utilitystone.command.tempban"],
        },
        "unban": {
            "description": "Lift a ban.",
            "usages": ["/unban <player: str>"],
            "permissions": ["utilitystone.command.unban"],
        },
        "mute": {
            "description": "Stop a player from using chat.",
            "usages": ["/mute <player: target> <duration: str> [reason: message]"],
            "permissions": ["utilitystone.command.mute"],
        },
        "unmute": {
            "description": "Let a muted player chat again.",
            "usages": ["/unmute <player: str>"],
            "permissions": ["utilitystone.command.unmute"],
        },
        "kit": {
            "description": "Claim a kit of items.",
            "usages": ["/kit [name: str]"],
            "permissions": ["utilitystone.command.kit"],
        },
        "kits": {
            "description": "List the kits you can claim.",
            "usages": ["/kits"],
            "permissions": ["utilitystone.command.kits"],
        },
        "who": {
            "description": "Show who is online.",
            "usages": ["/who"],
            "aliases": ["online"],
            "permissions": ["utilitystone.command.who"],
        },
        "ping": {
            "description": "Show connection latency.",
            "usages": ["/ping [player: target]"],
            "permissions": ["utilitystone.command.ping"],
        },
        "playtime": {
            "description": "Show how long someone has played.",
            "usages": ["/playtime [player: target]"],
            "permissions": ["utilitystone.command.playtime"],
        },
        "seen": {
            "description": "Show when a player was last online.",
            "usages": ["/seen <player: str>"],
            "permissions": ["utilitystone.command.seen"],
        },
        "whois": {
            "description": "Show detail about an online player.",
            "usages": ["/whois <player: target>"],
            "permissions": ["utilitystone.command.whois"],
        },
        "afk": {
            "description": "Mark yourself as away from keyboard.",
            "usages": ["/afk [reason: message]"],
            "permissions": ["utilitystone.command.afk"],
        },
        "utilitystone": {
            "description": "Show plugin status or reload the configuration.",
            "usages": ["/utilitystone (info|reload)[action: UtilityStoneAction]"],
            "aliases": ["ustone"],
            "permissions": ["utilitystone.command.utilitystone"],
        },
    }

    permissions = {
        "utilitystone.command.sethome": {"description": "Save a home.", "default": True},
        "utilitystone.command.home": {"description": "Travel to a home.", "default": True},
        "utilitystone.command.delhome": {"description": "Delete a home.", "default": True},
        "utilitystone.command.homes": {"description": "List your homes.", "default": True},
        "utilitystone.command.warp": {"description": "Use a warp.", "default": True},
        "utilitystone.command.warps": {"description": "List warps.", "default": True},
        "utilitystone.command.setwarp": {"description": "Create a warp.", "default": "op"},
        "utilitystone.command.delwarp": {"description": "Delete a warp.", "default": "op"},
        "utilitystone.command.spawn": {"description": "Travel to spawn.", "default": True},
        "utilitystone.command.setspawn": {"description": "Set the spawn point.", "default": "op"},
        "utilitystone.command.tpa": {"description": "Send a teleport request.", "default": True},
        "utilitystone.command.tpahere": {"description": "Send a summon request.", "default": True},
        "utilitystone.command.tpaccept": {"description": "Accept a teleport request.", "default": True},
        "utilitystone.command.tpdeny": {"description": "Deny a teleport request.", "default": True},
        "utilitystone.command.tpcancel": {"description": "Cancel your teleport request.", "default": True},
        "utilitystone.command.back": {"description": "Return to a previous position.", "default": True},
        "utilitystone.command.heal": {"description": "Restore health.", "default": "op"},
        "utilitystone.command.heal.others": {"description": "Heal another player.", "default": "op"},
        "utilitystone.command.feed": {"description": "Restore hunger.", "default": "op"},
        "utilitystone.command.feed.others": {"description": "Feed another player.", "default": "op"},
        "utilitystone.command.fly": {"description": "Toggle flight.", "default": "op"},
        "utilitystone.command.fly.others": {"description": "Toggle flight for others.", "default": "op"},
        "utilitystone.command.god": {"description": "Toggle damage immunity.", "default": "op"},
        "utilitystone.command.god.others": {"description": "Toggle immunity for others.", "default": "op"},
        "utilitystone.command.speed": {"description": "Change movement speed.", "default": "op"},
        "utilitystone.command.speed.others": {"description": "Change speed for others.", "default": "op"},
        "utilitystone.command.repair": {"description": "Repair a held item.", "default": "op"},
        "utilitystone.command.pm": {"description": "Send a private message.", "default": True},
        "utilitystone.command.reply": {"description": "Reply to a private message.", "default": True},
        "utilitystone.command.ignore": {"description": "Ignore a player.", "default": True},
        "utilitystone.command.unignore": {"description": "Stop ignoring a player.", "default": True},
        "utilitystone.command.ignorelist": {"description": "List ignored players.", "default": True},
        "utilitystone.command.broadcast": {"description": "Broadcast a message.", "default": "op"},
        "utilitystone.command.ban": {"description": "Ban a player.", "default": "op"},
        "utilitystone.command.tempban": {"description": "Temporarily ban a player.", "default": "op"},
        "utilitystone.command.unban": {"description": "Lift a ban.", "default": "op"},
        "utilitystone.command.mute": {"description": "Mute a player.", "default": "op"},
        "utilitystone.command.unmute": {"description": "Unmute a player.", "default": "op"},
        "utilitystone.command.kit": {"description": "Claim a kit.", "default": True},
        "utilitystone.command.kits": {"description": "List kits.", "default": True},
        "utilitystone.command.who": {"description": "See who is online.", "default": True},
        "utilitystone.command.ping": {"description": "See your latency.", "default": True},
        "utilitystone.command.ping.others": {"description": "See another latency.", "default": "op"},
        "utilitystone.command.playtime": {"description": "See your playtime.", "default": True},
        "utilitystone.command.playtime.others": {"description": "See another playtime.", "default": "op"},
        "utilitystone.command.seen": {"description": "See when a player was last online.", "default": True},
        "utilitystone.command.whois": {"description": "Inspect an online player.", "default": True},
        "utilitystone.command.afk": {"description": "Mark yourself away.", "default": True},
        "utilitystone.command.utilitystone": {"description": "Manage the plugin.", "default": "op"},
        "utilitystone.homes.unlimited": {"description": "Save homes without a limit.", "default": "op"},
        "utilitystone.teleport.instant": {"description": "Skip the teleport warmup.", "default": "op"},
        "utilitystone.teleport.nocooldown": {"description": "Skip the teleport cooldown.", "default": "op"},
        "utilitystone.chat.color": {"description": "Use colour codes in chat.", "default": "op"},
        "utilitystone.kit.tools": {"description": "Claim the tools kit.", "default": "op"},
    }

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.messages = Messages(self.settings)
        self.sessions = SessionRegistry()
        self.router: CommandRouter | None = None
        self.storage: StorageManager | None = None
        self.profiles: ProfileService | None = None
        self.homes: HomeService | None = None
        self.warps: WarpService | None = None
        self.spawns: SpawnService | None = None
        self.teleports: TeleportService | None = None
        self.punishments: PunishmentService | None = None
        self.kits: KitService | None = None
        self.afk: AfkService | None = None
        self.discord: DiscordBridge | None = None
        self.godPlayers: set = set()
        self._taskIds: list = []

    @property
    def pluginVersion(self) -> str:
        try:
            return self._get_description().version
        except Exception:
            return "unknown"

    def on_load(self) -> None:
        folder = Path(self.data_folder)
        folder.mkdir(parents=True, exist_ok=True)

        try:
            self.save_default_config()
            self.settings.applyFrom(self.config)
        except Exception as error:
            self.logger.error(f"Could not read config.toml, falling back to defaults: {error}")
            self.settings.applyFrom({})

    def on_enable(self) -> None:
        self.storage = StorageManager(self.data_folder, self.logger, self.settings.saveIntervalSeconds)

        self.profiles = ProfileService(self)
        self.homes = HomeService(self)
        self.warps = WarpService(self)
        self.spawns = SpawnService(self)
        self.teleports = TeleportService(self)
        self.punishments = PunishmentService(self)
        self.kits = KitService(self)
        self.afk = AfkService(self)
        self.discord = DiscordBridge(self)
        self.announceDiscord()

        self.router = CommandRouter(self.logger)
        for group in COMMAND_GROUPS:
            self.router.add(group(self))

        for listener in LISTENERS:
            self.register_events(listener(self))

        self.storage.start()
        self.scheduleTasks()

        self.discord.relayServerState("The server is online.")
        self.logger.info(
            f"Ready with {self.router.count} commands and a {self.settings.saveIntervalSeconds:g}s save cycle."
        )

    def on_disable(self) -> None:
        self.cancelTasks()

        if self.discord is not None:
            self.discord.stop("The server is shutting down.")

        if self.profiles is not None:
            self.profiles.syncPlaytime(self.server.online_players, self.sessions)

        if self.teleports is not None:
            self.teleports.clear()

        if self.storage is not None:
            self.storage.stop()

        self.sessions.clear()
        self.godPlayers.clear()
        self.logger.info("Everything saved and shut down cleanly.")

    def on_command(self, sender, command, args: list) -> bool:
        if self.router is None:
            return False
        return self.router.dispatch(sender, command.name, args)

    def reloadSettings(self) -> bool:
        try:
            self.settings.applyFrom(self.reload_config())
        except Exception as error:
            self.logger.error(f"Reload failed, keeping the settings already in memory: {error}")
            return False

        if self.storage is not None:
            self.storage.intervalSeconds = min(900.0, max(5.0, self.settings.saveIntervalSeconds))

        if self.discord is not None:
            self.discord.stop()
            self.announceDiscord()

        self.cancelTasks()
        self.scheduleTasks()
        return True

    def scheduleTasks(self) -> None:
        scheduler = self.server.scheduler

        teleportTask = scheduler.run_task(
            self, self.teleports.tick, delay=20, period=self.settings.teleportPollTicks
        )
        self._taskIds.append(teleportTask.task_id)

        afkTicks = max(20, int(self.settings.afkSampleSeconds * 20))
        afkTask = scheduler.run_task(self, self.afk.sample, delay=afkTicks, period=afkTicks)
        self._taskIds.append(afkTask.task_id)

        syncTicks = max(300, int(self.settings.playtimeSyncSeconds * 20))
        syncTask = scheduler.run_task(self, self.syncPlaytime, delay=syncTicks, period=syncTicks)
        self._taskIds.append(syncTask.task_id)

        if self.discord is not None and self.discord.active:
            discordTicks = self.settings.discordPollTicks
            discordTask = scheduler.run_task(
                self, self.discord.drainInbound, delay=discordTicks, period=discordTicks
            )
            self._taskIds.append(discordTask.task_id)

    def cancelTasks(self) -> None:
        scheduler = self.server.scheduler
        for taskId in self._taskIds:
            scheduler.cancel_task(taskId)
        self._taskIds.clear()

    def announceDiscord(self) -> None:
        self.discord.configure()
        for line in self.discord.statusLines():
            self.logger.info(line)
        self.discord.start()

    def syncPlaytime(self) -> None:
        self.profiles.syncPlaytime(self.server.online_players, self.sessions)

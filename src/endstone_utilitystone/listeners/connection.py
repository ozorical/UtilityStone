from endstone.event import EventPriority, PlayerJoinEvent, PlayerQuitEvent, event_handler

from endstone_utilitystone.util.text import colorize

SUPPRESS_TOKENS = frozenset({"none", "off", "hidden", "silent"})


class ConnectionListener:
    def __init__(self, plugin):
        self.plugin = plugin

    @event_handler(priority=EventPriority.LOW)
    def onPlayerJoin(self, event: PlayerJoinEvent) -> None:
        player = event.player
        plugin = self.plugin

        session = plugin.sessions.open(player)
        plugin.profiles.recordJoin(player)

        template = plugin.settings.joinMessage
        if template:
            event.join_message = None if template.lower() in SUPPRESS_TOKENS else self.render(template, player)

        welcome = plugin.settings.welcomeMessage
        if welcome:
            player.send_message(colorize(welcome.replace("{name}", player.name)))

        if plugin.settings.spawnOnFirstJoin and plugin.spawns.markSeen(player):
            plugin.server.scheduler.run_task(plugin, lambda: self.sendToSpawn(player), delay=20)

        plugin.discord.relayPresence(f"{player.name} joined the server.")
        session.touch()

    @event_handler(priority=EventPriority.LOW)
    def onPlayerQuit(self, event: PlayerQuitEvent) -> None:
        player = event.player
        plugin = self.plugin

        session = plugin.sessions.close(player)
        plugin.profiles.recordQuit(player, session)
        plugin.teleports.forget(player)
        plugin.godPlayers.discard(player.unique_id)

        plugin.discord.relayPresence(f"{player.name} left the server.")

        template = plugin.settings.quitMessage
        if template:
            event.quit_message = None if template.lower() in SUPPRESS_TOKENS else self.render(template, player)

    def sendToSpawn(self, player) -> None:
        try:
            if not player.is_valid:
                return
        except Exception:
            return

        destination = self.plugin.spawns.resolve()
        if destination is not None:
            player.teleport(destination)

    def render(self, template: str, player) -> str:
        return colorize(template.replace("{name}", player.name))

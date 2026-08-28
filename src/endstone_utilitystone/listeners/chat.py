from endstone.event import EventPriority, PlayerChatEvent, PlayerCommandEvent, event_handler

from endstone_utilitystone.util.durations import formatDuration
from endstone_utilitystone.util.text import colorize, stripColors

COLOR_PERMISSION = "utilitystone.chat.color"
AFK_COMMANDS = ("/afk", "afk")


class ChatListener:
    def __init__(self, plugin):
        self.plugin = plugin

    @event_handler(priority=EventPriority.HIGH, ignore_cancelled=True)
    def onPlayerChat(self, event: PlayerChatEvent) -> None:
        plugin = self.plugin
        player = event.player
        session = plugin.sessions.of(player)

        mute = plugin.punishments.muteFor(str(player.unique_id))
        if mute is not None:
            event.cancel()
            remaining = plugin.punishments.remainingMute(mute)
            plugin.messages.failure(player, f"You are muted for another {formatDuration(remaining)}.")
            return

        plugin.afk.touch(player, session)
        plugin.discord.relayChat(player.name, event.message)

        if not plugin.settings.chatManaged:
            return

        event.cancel()
        self.deliver(player, session, event.message)

    @event_handler(priority=EventPriority.MONITOR, ignore_cancelled=True)
    def onPlayerCommand(self, event: PlayerCommandEvent) -> None:
        command = event.command.lstrip("/").split(" ", 1)[0].lower()
        if command == "afk":
            return

        self.plugin.afk.touch(event.player)

    def deliver(self, player, session, message: str) -> None:
        plugin = self.plugin
        settings = plugin.settings
        profiles = plugin.profiles
        sessions = plugin.sessions

        body = colorize(message) if player.has_permission(COLOR_PERMISSION) else message
        template = colorize(plugin.afk.tag(session) + settings.chatFormat)
        line = template.replace("{name}", player.name).replace("{message}", body)

        senderKey = session.key if session is not None else str(player.unique_id)

        for recipient in plugin.server.online_players:
            recipientSession = sessions.of(recipient)
            recipientKey = recipientSession.key if recipientSession is not None else str(recipient.unique_id)
            if recipientKey != senderKey and profiles.isIgnoring(recipientKey, senderKey):
                continue
            recipient.send_message(line)

        plugin.server.logger.info(stripColors(line))

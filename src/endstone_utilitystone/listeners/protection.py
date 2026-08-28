from endstone import Player
from endstone.event import ActorDamageEvent, EventPriority, PlayerDeathEvent, event_handler

from endstone_utilitystone.util.text import stripColors


class ProtectionListener:
    def __init__(self, plugin):
        self.plugin = plugin

    @event_handler(priority=EventPriority.HIGHEST, ignore_cancelled=True)
    def onActorDamage(self, event: ActorDamageEvent) -> None:
        protected = self.plugin.godPlayers
        if not protected:
            return

        actor = event.actor
        if not isinstance(actor, Player):
            return

        if actor.unique_id in protected:
            event.cancel()

    @event_handler(priority=EventPriority.MONITOR)
    def onPlayerDeath(self, event: PlayerDeathEvent) -> None:
        if self.plugin.settings.backOnDeath:
            self.plugin.teleports.rememberLocation(event.player)

        self.plugin.discord.relayDeath(self.deathText(event))

    def deathText(self, event: PlayerDeathEvent) -> str:
        message = event.death_message

        if isinstance(message, str) and message.strip():
            return stripColors(message.strip())

        if message is not None:
            try:
                return stripColors(self.plugin.server.language.translate(message))
            except Exception:
                pass

        return f"{event.player.name} died."

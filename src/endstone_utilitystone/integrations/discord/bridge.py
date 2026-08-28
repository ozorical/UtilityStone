from __future__ import annotations

import asyncio
from collections import deque
from pathlib import Path

from endstone_utilitystone.integrations.discord.env import loadEnvironment
from endstone_utilitystone.util.text import colorize, stripColors

TOKEN_KEY = "DISCORD_BOT_TOKEN"
CHANNEL_KEY = "DISCORD_CHANNEL_ID"

STATE_DISABLED = "disabled"
STATE_UNCONFIGURED = "unconfigured"
STATE_UNAVAILABLE = "unavailable"
STATE_READY = "ready"

OUTBOUND_LIMIT = 400
INBOUND_LIMIT = 200
DISCORD_MESSAGE_LIMIT = 1900


class DiscordBridge:
    def __init__(self, plugin):
        self.plugin = plugin
        self.state = STATE_DISABLED
        self.token = ""
        self.channelId = ""
        self.channelName = ""
        self.connected = False
        self._outbound = deque(maxlen=OUTBOUND_LIMIT)
        self._inbound = deque(maxlen=INBOUND_LIMIT)
        self._gateway = None
        self._future = None
        self._running = False

    @property
    def active(self) -> bool:
        return self._running and self.state == STATE_READY

    def envPaths(self) -> list:
        return [Path(self.plugin.data_folder) / ".env", Path.cwd() / ".env"]

    def configure(self) -> str:
        settings = self.plugin.settings

        if not settings.discordEnabled:
            self.state = STATE_DISABLED
            return self.state

        values = loadEnvironment(self.envPaths())
        self.token = str(values.get(TOKEN_KEY, "")).strip()
        self.channelId = str(values.get(CHANNEL_KEY, "")).strip()

        if not self.token or not self.channelId:
            self.state = STATE_UNCONFIGURED
            return self.state

        if not self.channelId.isdigit():
            self.plugin.logger.warning(f"{CHANNEL_KEY} should be the numeric channel id, not a channel name.")
            self.state = STATE_UNCONFIGURED
            return self.state

        try:
            import aiohttp
        except ImportError:
            self.state = STATE_UNAVAILABLE
            return self.state

        self.state = STATE_READY
        return self.state

    def start(self) -> None:
        if self.state != STATE_READY or self._running:
            return

        from endstone.asyncio import submit

        self._running = True
        self._future = submit(self.runBridge())

    def stop(self, farewell: str = "") -> None:
        if farewell and self.connected and self.plugin.settings.discordRelayServerState:
            self.sendFinalMessage(self.plugin.settings.discordEventFormat.replace("{message}", farewell))

        self._running = False

        if self._gateway is not None:
            self._gateway.stop()

        future = self._future
        self._future = None

        if future is not None:
            future.cancel()
            try:
                future.result(timeout=5.0)
            except Exception:
                pass

        self.connected = False
        self._outbound.clear()
        self._inbound.clear()

    def relay(self, text: str) -> None:
        if not self.active or not text:
            return
        self._outbound.append(stripColors(colorize(text)))

    def relayChat(self, name: str, message: str) -> None:
        if not self.plugin.settings.discordRelayChat:
            return
        self.relay(self.plugin.settings.discordChatFormat.replace("{name}", name).replace("{message}", message))

    def relayEvent(self, text: str) -> None:
        self.relay(self.plugin.settings.discordEventFormat.replace("{message}", text))

    def relayDeath(self, text: str) -> None:
        if not self.plugin.settings.discordRelayDeaths:
            return
        self.relayEvent(text)

    def relayPresence(self, text: str) -> None:
        if not self.plugin.settings.discordRelayJoinLeave:
            return
        self.relayEvent(text)

    def relayServerState(self, text: str) -> None:
        if not self.plugin.settings.discordRelayServerState:
            return
        self.relayEvent(text)

    def receiveFromDiscord(self, channelId: str, name: str, content: str) -> None:
        if channelId != self.channelId:
            return
        self._inbound.append((name, content))

    def drainInbound(self) -> None:
        if not self._inbound:
            return

        settings = self.plugin.settings
        server = self.plugin.server
        limit = settings.discordInboundLimit

        while self._inbound:
            try:
                name, content = self._inbound.popleft()
            except IndexError:
                return

            body = " ".join(stripColors(content).split())
            if len(body) > limit:
                body = body[: max(1, limit - 3)] + "..."

            line = colorize(settings.discordInboundFormat).replace("{name}", name).replace("{message}", body)
            server.broadcast_message(line)

    async def runBridge(self) -> None:
        import aiohttp

        from endstone_utilitystone.integrations.discord.gateway import DiscordGateway
        from endstone_utilitystone.integrations.discord.rest import DiscordRest

        logger = self.plugin.logger
        timeout = aiohttp.ClientTimeout(total=30.0)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            rest = DiscordRest(session, self.token, logger)

            identity, problem = await rest.identity()
            if problem is not None:
                logger.error(f"Discord relay could not start. {problem}")
                self.connected = False
                return

            name, problem = await rest.channelName(self.channelId)
            if problem is not None:
                logger.error(f"Discord relay could not start. {problem}")
                self.connected = False
                return

            self.channelName = name
            self.connected = True
            logger.info(
                f"Discord relay linked as {identity.get('username', 'bot')} to channel #{name}."
            )

            self._gateway = DiscordGateway(
                session, self.token, logger, self.receiveFromDiscord, self.onGatewayReady
            )

            sender = asyncio.create_task(self.pumpOutbound(rest))
            listener = asyncio.create_task(self._gateway.run())

            try:
                await asyncio.gather(sender, listener)
            except asyncio.CancelledError:
                raise
            finally:
                for task in (sender, listener):
                    task.cancel()
                self.connected = False

    def sendFinalMessage(self, text: str) -> None:
        from endstone.asyncio import submit

        try:
            future = submit(self.postDirect(stripColors(colorize(text))))
            future.result(timeout=5.0)
        except Exception:
            pass

    async def postDirect(self, content: str) -> None:
        import aiohttp

        from endstone_utilitystone.integrations.discord.rest import DiscordRest

        timeout = aiohttp.ClientTimeout(total=5.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            rest = DiscordRest(session, self.token, self.plugin.logger)
            await rest.sendMessage(self.channelId, content)

    def onGatewayReady(self, username: str) -> None:
        self.plugin.logger.info(f"Discord gateway ready as {username}.")

    async def pumpOutbound(self, rest) -> None:
        interval = max(0.5, self.plugin.settings.discordSendIntervalSeconds)

        while self._running:
            await asyncio.sleep(interval)

            if not self._outbound:
                continue

            lines = []
            length = 0
            while self._outbound:
                line = self._outbound[0]
                if lines and length + len(line) + 1 > DISCORD_MESSAGE_LIMIT:
                    break

                self._outbound.popleft()
                lines.append(line[:DISCORD_MESSAGE_LIMIT])
                length += len(line) + 1

            if lines:
                await rest.sendMessage(self.channelId, "\n".join(lines))

    def statusLines(self) -> list:
        if self.state == STATE_DISABLED:
            return ["Discord relay is switched off in config.toml."]

        if self.state == STATE_UNAVAILABLE:
            return ["Discord relay needs the aiohttp package, which was not found in this Python environment."]

        if self.state == STATE_UNCONFIGURED:
            folder = Path(self.plugin.data_folder) / ".env"
            return [
                "Discord relay is available but not set up, which is fine. The plugin runs without it.",
                f"To switch it on, create {folder} with these two lines:",
                f"  {TOKEN_KEY}=your-bot-token",
                f"  {CHANNEL_KEY}=your-channel-id",
                "The README has a step by step setup guide.",
            ]

        target = f"#{self.channelName}" if self.channelName else self.channelId
        return [f"Discord relay is set up for channel {target}."]

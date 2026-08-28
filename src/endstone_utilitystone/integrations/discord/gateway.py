from __future__ import annotations

import asyncio
import random

from aiohttp import WSMsgType

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"

INTENT_GUILDS = 1 << 0
INTENT_GUILD_MESSAGES = 1 << 9
INTENT_MESSAGE_CONTENT = 1 << 15
INTENTS = INTENT_GUILDS | INTENT_GUILD_MESSAGES | INTENT_MESSAGE_CONTENT

OP_DISPATCH = 0
OP_HEARTBEAT = 1
OP_IDENTIFY = 2
OP_RECONNECT = 7
OP_INVALID_SESSION = 9
OP_HELLO = 10
OP_HEARTBEAT_ACK = 11

MIN_BACKOFF = 2.0
MAX_BACKOFF = 120.0


class DiscordGateway:
    def __init__(self, session, token: str, logger, onMessage, onReady=None):
        self.session = session
        self.token = token
        self.logger = logger
        self.onMessage = onMessage
        self.onReady = onReady
        self.sequence = None
        self.botUserId = None
        self.running = True

    def stop(self) -> None:
        self.running = False

    async def run(self) -> None:
        backoff = MIN_BACKOFF

        while self.running:
            try:
                await self.connectOnce()
                backoff = MIN_BACKOFF
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.logger.warning(f"Discord gateway dropped, retrying in {backoff:.0f}s: {error}")

            if not self.running:
                return

            await asyncio.sleep(backoff + random.uniform(0.0, 1.0))
            backoff = min(MAX_BACKOFF, backoff * 2.0)

    async def connectOnce(self) -> None:
        async with self.session.ws_connect(GATEWAY_URL, heartbeat=None, autoping=True) as socket:
            hello = await socket.receive_json()
            if hello.get("op") != OP_HELLO:
                raise RuntimeError("Discord did not send the expected hello frame")

            interval = float(hello["d"]["heartbeat_interval"]) / 1000.0
            await socket.send_json(self.identifyPayload())

            beat = asyncio.create_task(self.heartbeat(socket, interval))
            try:
                async for frame in socket:
                    if frame.type is not WSMsgType.TEXT:
                        continue

                    payload = frame.json()
                    if not await self.handleFrame(socket, payload):
                        return
            finally:
                beat.cancel()
                try:
                    await beat
                except (asyncio.CancelledError, Exception):
                    pass

    def identifyPayload(self) -> dict:
        return {
            "op": OP_IDENTIFY,
            "d": {
                "token": self.token,
                "intents": INTENTS,
                "properties": {"os": "endstone", "browser": "utilitystone", "device": "utilitystone"},
                "presence": {"status": "online", "afk": False, "activities": []},
            },
        }

    async def heartbeat(self, socket, interval: float) -> None:
        await asyncio.sleep(interval * random.uniform(0.1, 0.9))
        while self.running and not socket.closed:
            await socket.send_json({"op": OP_HEARTBEAT, "d": self.sequence})
            await asyncio.sleep(interval)

    async def handleFrame(self, socket, payload: dict) -> bool:
        opcode = payload.get("op")

        if payload.get("s") is not None:
            self.sequence = payload["s"]

        if opcode == OP_HEARTBEAT:
            await socket.send_json({"op": OP_HEARTBEAT, "d": self.sequence})
            return True

        if opcode in (OP_RECONNECT, OP_INVALID_SESSION):
            self.sequence = None
            return False

        if opcode != OP_DISPATCH:
            return True

        name = payload.get("t")
        data = payload.get("d") or {}

        if name == "READY":
            user = data.get("user") or {}
            self.botUserId = str(user.get("id", ""))
            if self.onReady is not None:
                self.onReady(user.get("username", "bot"))
            return True

        if name == "MESSAGE_CREATE":
            self.dispatchMessage(data)

        return True

    def dispatchMessage(self, data: dict) -> None:
        author = data.get("author") or {}
        authorId = str(author.get("id", ""))

        if not authorId or authorId == self.botUserId:
            return

        if author.get("bot") or data.get("webhook_id"):
            return

        content = (data.get("content") or "").strip()
        attachments = data.get("attachments") or []
        if not content and attachments:
            content = f"[sent {len(attachments)} attachment(s)]"

        if not content:
            return

        member = data.get("member") or {}
        name = member.get("nick") or author.get("global_name") or author.get("username") or "unknown"

        self.onMessage(str(data.get("channel_id", "")), str(name), content)

from __future__ import annotations

import asyncio

API_BASE = "https://discord.com/api/v10"
USER_AGENT = "DiscordBot (https://github.com/ozz/utilitystone, 1.0.0)"
NO_MENTIONS = {"parse": []}


class DiscordRest:
    def __init__(self, session, token: str, logger):
        self.session = session
        self.token = token
        self.logger = logger

    def headers(self) -> dict:
        return {
            "Authorization": f"Bot {self.token}",
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        }

    async def identity(self):
        try:
            async with self.session.get(f"{API_BASE}/users/@me", headers=self.headers()) as response:
                if response.status == 401:
                    return None, "The bot token was rejected. Check DISCORD_BOT_TOKEN."
                if response.status != 200:
                    return None, f"Discord returned status {response.status} while checking the bot token."
                return await response.json(), None
        except asyncio.CancelledError:
            raise
        except Exception as error:
            return None, f"Could not reach Discord: {error}"

    async def channelName(self, channelId: str):
        try:
            async with self.session.get(f"{API_BASE}/channels/{channelId}", headers=self.headers()) as response:
                if response.status in (403, 404):
                    return None, (
                        f"The bot cannot see channel {channelId}. Invite it to the server and give it "
                        "View Channel, Send Messages and Read Message History."
                    )
                if response.status != 200:
                    return None, f"Discord returned status {response.status} while checking the channel."
                payload = await response.json()
                return payload.get("name", channelId), None
        except asyncio.CancelledError:
            raise
        except Exception as error:
            return None, f"Could not reach Discord: {error}"

    async def sendMessage(self, channelId: str, content: str) -> bool:
        payload = {"content": content, "allowed_mentions": NO_MENTIONS}
        url = f"{API_BASE}/channels/{channelId}/messages"

        for attempt in range(3):
            try:
                async with self.session.post(url, headers=self.headers(), json=payload) as response:
                    if response.status in (200, 201):
                        return True

                    if response.status == 429:
                        body = await response.json(content_type=None)
                        delay = float(body.get("retry_after", 1.0)) if isinstance(body, dict) else 1.0
                        await asyncio.sleep(min(30.0, delay + 0.1))
                        continue

                    if response.status in (401, 403, 404):
                        self.logger.warning(
                            f"Discord refused a relayed message with status {response.status}. "
                            "Check the bot token and channel permissions."
                        )
                        return False

                    if 500 <= response.status < 600:
                        await asyncio.sleep(1.0 + attempt)
                        continue

                    self.logger.warning(f"Discord returned status {response.status} for a relayed message.")
                    return False
            except asyncio.CancelledError:
                raise
            except Exception as error:
                if attempt == 2:
                    self.logger.warning(f"Could not deliver a message to Discord: {error}")
                    return False
                await asyncio.sleep(1.0 + attempt)

        return False

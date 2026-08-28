# UtilityStone

UtilityStone is an essentials style toolkit for [Endstone](https://endstone.dev) servers. It is a spin off of
the Minecraft Essentials add on, rebuilt from scratch against the Endstone Python API so that it stays quick on
a busy realm rather than on an empty test world. It also ships an optional two way Discord chat relay.

The whole plugin is built around one rule: work that happens once per command is cheap, work that happens once
per tick is not. Nothing in UtilityStone runs on a per movement or per tick basis, and nothing writes to disk
while the server thread is waiting.

Created by Ozz. Released under the MIT licence, so you are free to copy, change and redistribute it as long as
the copyright notice and licence stay with it.

## Requirements

- Endstone 0.11 or newer (built and tested against 0.11.9, Minecraft Bedrock 26.44)
- Python 3.10 or newer

UtilityStone has no third party dependencies. The Discord relay uses aiohttp, which already ships with
Endstone, so there is nothing extra to install.

## Installing

1. Download or build `endstone_utilitystone-1.0.1-py3-none-any.whl`.
2. Drop the wheel into your server `plugins` folder.
3. Start the server. UtilityStone writes `plugins/utilitystone/config.toml` on first run.
4. Edit the config if you want, then run `/utilitystone reload`.

To build the wheel yourself:

```
pip install build
python -m build --wheel
```

## Commands

Every command is listed with the permission that guards it. Arguments in `<angle brackets>` are required and
arguments in `[square brackets]` are optional.

### Homes

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/sethome [name]` | `utilitystone.command.sethome` | everyone | Saves where you stand. The name defaults to `home`. |
| `/home [name]` | `utilitystone.command.home` | everyone | Travels to a home. With one home saved the name is optional. |
| `/delhome <name>` | `utilitystone.command.delhome` | everyone | Deletes a home. |
| `/homes` | `utilitystone.command.homes` | everyone | Lists your homes and how many you have left. |

### Warps and spawn

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/warp [name]` | `utilitystone.command.warp` | everyone | Travels to a warp, or lists warps when the name is left off. |
| `/warps` | `utilitystone.command.warps` | everyone | Lists the warps you are allowed to use. |
| `/setwarp <name>` | `utilitystone.command.setwarp` | operator | Creates or moves a warp. |
| `/delwarp <name>` | `utilitystone.command.delwarp` | operator | Deletes a warp. |
| `/spawn` | `utilitystone.command.spawn` | everyone | Travels to the spawn point. |
| `/setspawn` | `utilitystone.command.setspawn` | operator | Sets the spawn point to where you stand. |

### Teleporting

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/tpa <player>` | `utilitystone.command.tpa` | everyone | Asks to teleport to somebody. |
| `/tpahere <player>` | `utilitystone.command.tpahere` | everyone | Asks somebody to teleport to you. |
| `/tpaccept [player]` | `utilitystone.command.tpaccept` | everyone | Accepts a request. Alias `/tpyes`. |
| `/tpdeny [player]` | `utilitystone.command.tpdeny` | everyone | Turns a request down. Alias `/tpno`. |
| `/tpcancel` | `utilitystone.command.tpcancel` | everyone | Withdraws the request you sent. |
| `/back` | `utilitystone.command.back` | everyone | Returns to where you last teleported from, or where you died. |

### Player state

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/heal [player]` | `utilitystone.command.heal` | operator | Refills health. |
| `/feed [player]` | `utilitystone.command.feed` | operator | Refills hunger. |
| `/fly [player]` | `utilitystone.command.fly` | operator | Toggles flight. |
| `/god [player]` | `utilitystone.command.god` | operator | Toggles damage immunity. |
| `/speed <amount> [player]` | `utilitystone.command.speed` | operator | Sets walk or fly speed from 0.1 to 10. |
| `/repair` | `utilitystone.command.repair` | operator | Repairs the item in your main hand. |

Running any of these on somebody else needs the matching `.others` permission, for example
`utilitystone.command.heal.others`.

### Chat and messaging

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/pm <player> <message>` | `utilitystone.command.pm` | everyone | Sends a private message. Alias `/dm`. |
| `/reply <message>` | `utilitystone.command.reply` | everyone | Replies to the last message you got. Alias `/r`. |
| `/ignore <player>` | `utilitystone.command.ignore` | everyone | Hides that player from your chat and blocks their private messages. |
| `/unignore <player>` | `utilitystone.command.unignore` | everyone | Undoes an ignore. |
| `/ignorelist` | `utilitystone.command.ignorelist` | everyone | Lists who you are ignoring. |
| `/broadcast <message>` | `utilitystone.command.broadcast` | operator | Sends a highlighted message to everyone. |

### Moderation

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/tempban <player> <duration> [reason]` | `utilitystone.command.tempban` | operator | Bans for a set length, or `perm` for good. |
| `/mute <player> <duration> [reason]` | `utilitystone.command.mute` | operator | Blocks a player from chatting. |
| `/unmute <player>` | `utilitystone.command.unmute` | operator | Lets a muted player chat again. |

Bedrock already provides `/ban` and `/unban`, so UtilityStone does not replace them. `/tempban` adds the
timed bans vanilla lacks, and accepts `perm` when you want a permanent ban with a reason attached. All of
them write to the same server ban list, so vanilla `/unban` lifts a UtilityStone ban and the entries survive
restarts. Mutes are stored by UtilityStone and expire on their own.

Durations accept `30s`, `15m`, `2h`, `7d`, `3w`, `1mo`, `1y` and combinations such as `1d12h`. A bare number is
read as minutes. Use `perm` or `forever` for something that never expires.

### Kits

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/kit [name]` | `utilitystone.command.kit` | everyone | Claims a kit, or lists kits when the name is left off. |
| `/kits` | `utilitystone.command.kits` | everyone | Lists the kits you can claim. |

### Information

| Command | Permission | Default | What it does |
| --- | --- | --- | --- |
| `/who` | `utilitystone.command.who` | everyone | Lists who is online and who is AFK. Alias `/online`. |
| `/ping [player]` | `utilitystone.command.ping` | everyone | Shows connection latency. |
| `/playtime [player]` | `utilitystone.command.playtime` | everyone | Shows total time played. |
| `/seen <player>` | `utilitystone.command.seen` | everyone | Shows when somebody was last online. Works offline. |
| `/whois <player>` | `utilitystone.command.whois` | everyone | Shows detail about an online player. |
| `/afk [reason]` | `utilitystone.command.afk` | everyone | Marks you as away. |
| `/utilitystone [info\|reload]` | `utilitystone.command.utilitystone` | operator | Shows status or reloads the config. Alias `/ustone`. |

### Extra permissions

| Permission | Default | What it grants |
| --- | --- | --- |
| `utilitystone.homes.unlimited` | operator | Saves homes with no limit. |
| `utilitystone.teleport.instant` | operator | Skips the teleport warmup. |
| `utilitystone.teleport.nocooldown` | operator | Skips the teleport cooldown. |
| `utilitystone.chat.color` | operator | Uses `&` colour codes in chat. |
| `utilitystone.kit.tools` | operator | Claims the example `tools` kit. |

## Commands that are deliberately missing

Bedrock already ships `/kick`, `/list`, `/msg`, `/tell`, `/w`, `/tp`, `/ban` and `/unban`. UtilityStone does
not register any of those names, because taking over a vanilla command is a good way to break the client side
command tree for every player on the server. The replacements are `/who` for `/list` and `/pm` plus `/reply`
for messaging. Kicking, coordinate teleports and permanent bans stay on the vanilla commands, which already
work, and `/tempban` covers the timed bans vanilla does not offer.

## Configuration

The config lives at `plugins/utilitystone/config.toml`. Run `/utilitystone reload` after editing. A reload
rereads every value and restarts the background tasks, so poll intervals take effect straight away.

### `[storage]`

| Key | Default | Meaning |
| --- | --- | --- |
| `saveIntervalSeconds` | `30` | How often the background writer flushes changed data. Clamped to 5 to 900. |
| `playtimeSyncSeconds` | `120` | How often playtime totals are written for online players, so a crash costs little. |

### `[messages]`

| Key | Default | Meaning |
| --- | --- | --- |
| `usePrefix` | `true` | Whether plugin replies carry a prefix. |
| `prefix` | `&8[&bUtilityStone&8]&r ` | The prefix itself. Supports `&` colour codes. |

### `[homes]`

| Key | Default | Meaning |
| --- | --- | --- |
| `defaultLimit` | `3` | Homes everybody may save. |

`[homes.limits]` maps a permission node to a larger allowance. A player gets the highest limit they hold. The
shipped example gives `utilitystone.homes.vip` eight homes and `utilitystone.homes.staff` twenty. Neither node
is granted by default, so wire them up in whatever permission manager you use.

### `[warps]`

| Key | Default | Meaning |
| --- | --- | --- |
| `requirePerWarpPermission` | `false` | When true, each warp needs `utilitystone.warp.<name>`. |

### `[spawn]`

| Key | Default | Meaning |
| --- | --- | --- |
| `teleportOnFirstJoin` | `false` | Sends brand new players to the spawn point one second after they join. |

### `[teleport]`

| Key | Default | Meaning |
| --- | --- | --- |
| `warmupSeconds` | `3` | Delay before a teleport fires. Set to `0` to teleport instantly. |
| `cooldownSeconds` | `5` | Wait between teleports. |
| `requestTimeoutSeconds` | `60` | How long a `/tpa` request stays open. |
| `cancelOnMove` | `true` | Cancels the warmup if the player walks off. |
| `moveTolerance` | `0.75` | How far a player may drift during a warmup, in blocks. |
| `pollTicks` | `10` | How often warmups and request expiry are checked. Ten ticks is twice a second. |
| `rememberDeathLocation` | `true` | Lets `/back` return you to where you died. |
| `historySize` | `5` | How many previous positions `/back` remembers per player. |

### `[chat]`

| Key | Default | Meaning |
| --- | --- | --- |
| `manageFormat` | `true` | Lets UtilityStone deliver chat itself. |
| `format` | `<{name}> {message}` | Chat layout. `{name}` and `{message}` are replaced. |
| `afkTag` | `&7[AFK] &r` | Prefix shown in front of an AFK player's chat. |

The Endstone API hands out the chat recipient list as a copy, so a plugin cannot quietly drop one reader from a
normal chat message. To make `/ignore` actually work on public chat, UtilityStone cancels the event and sends
the line itself to everybody who is not ignoring the speaker. The default format matches vanilla, so players
will not notice a difference. Set `manageFormat` to `false` if another plugin owns your chat, and be aware that
`/ignore` will then only apply to private messages.

### `[afk]`

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `true` | Turns automatic AFK detection on. |
| `timeoutSeconds` | `300` | Idle time before somebody is marked away. |
| `sampleSeconds` | `5` | How often positions are sampled. |
| `announce` | `true` | Announces AFK changes in chat. |

### `[connection]`

| Key | Default | Meaning |
| --- | --- | --- |
| `joinMessage` | empty | Custom join message. `{name}` is replaced. Empty keeps the server default, `none` hides it. |
| `quitMessage` | empty | Same, for leaving. |
| `welcomeMessage` | empty | Private message sent to a player as they join. |

### Kits

Each kit is its own table, so `[kits.starter]` defines a kit called `starter`.

```toml
[kits.starter]
cooldown = "24h"
items = [
    { type = "minecraft:stone_sword", amount = 1 },
    { type = "minecraft:bread", amount = 16 },
]

[kits.tools]
permission = "utilitystone.kit.tools"
cooldown = "7d"
items = [
    { type = "minecraft:diamond_pickaxe", amount = 1, name = "&bStone Cutter", enchants = { efficiency = 3, unbreaking = 2 } },
]
```

| Key | Required | Meaning |
| --- | --- | --- |
| `items` | yes | List of items. `type` is required, `amount`, `name`, `lore` and `enchants` are optional. |
| `cooldown` | no | Wait between claims, in the usual duration format. Leave it out for no cooldown. |
| `permission` | no | Node needed to claim the kit. Leave it out and everybody may claim it. |

If a kit sets a `permission` that UtilityStone does not ship, nobody holds it until you grant it. That is
deliberate. Adding your own nodes to the plugin is not possible at runtime with the current Endstone API, so
point `permission` at a node your permission manager already knows about, or leave it off entirely.

Anything that does not fit in a player's inventory is dropped at their feet rather than lost.

## Discord relay

UtilityStone can mirror your in game chat into a Discord channel and carry Discord messages back into the game.
It is an optional module. If you never set it up, nothing changes: the plugin loads, every command works, and
the console prints a short note telling you the relay is available if you want it. No token and no channel id
are required for the plugin to run.

What gets relayed to Discord:

- Chat messages from players
- Death messages
- Join and leave messages
- Server start and shutdown

What comes back into the game: any normal message posted in the linked channel, shown to every player as
`[Discord] Name: message`. Messages from bots, webhooks and from UtilityStone's own bot are ignored, so the
relay cannot talk to itself in a loop.

### Setup guide

**1. Make a Discord application**

Go to [discord.com/developers/applications](https://discord.com/developers/applications) and press
**New Application**. Give it a name such as `UtilityStone`.

**2. Add a bot and copy the token**

Open the **Bot** tab. Press **Reset Token**, then **Copy**. This is your `DISCORD_BOT_TOKEN`. Treat it like a
password: anyone holding it controls the bot. If you ever paste it somewhere public, reset it immediately.

**3. Turn on the message content intent**

Still on the **Bot** tab, scroll to **Privileged Gateway Intents** and switch on **MESSAGE CONTENT INTENT**.
Without it Discord sends your bot empty message bodies, so nothing reaches the game. This is the step people
miss most often.

**4. Invite the bot to your server**

Open **OAuth2**, then **URL Generator**. Tick the `bot` scope, then tick these bot permissions:

- View Channel
- Send Messages
- Read Message History

Copy the generated URL, open it in a browser, and pick the Discord server you want.

**5. Get the channel id**

In Discord, open **User Settings**, then **Advanced**, and turn on **Developer Mode**. Right click the channel
you want to use and choose **Copy Channel ID**. It is a long number such as `112233445566778899`. That is your
`DISCORD_CHANNEL_ID`. It is the numeric id, not the channel name.

**6. Create the .env file**

Make a file called `.env` inside `plugins/utilitystone/` next to `config.toml`:

```
DISCORD_BOT_TOKEN=your-bot-token-here
DISCORD_CHANNEL_ID=112233445566778899
```

There is an `.env.example` in this repository you can copy. UtilityStone also reads a `.env` in the server root
folder if there is not one in the plugin folder, and real environment variables of the same names win over
either file, which is handy for hosting panels and Docker.

**7. Start the relay**

Restart the server, or run `/utilitystone reload`. You should see this in the console:

```
[UtilityStone] Discord relay linked as UtilityStone to channel #minecraft.
[UtilityStone] Discord gateway ready as UtilityStone.
```

Run `/utilitystone info` in game and the **Discord relay** line will read `connected`.

### If it does not connect

| Console message | What to do |
| --- | --- |
| `The bot token was rejected` | The token is wrong or was reset. Copy it again from the Bot tab. |
| `The bot cannot see channel ...` | Invite the bot to that Discord server and give it View Channel, Send Messages and Read Message History. |
| `DISCORD_CHANNEL_ID should be the numeric channel id` | You used the channel name. Turn on Developer Mode and copy the id instead. |
| Chat reaches Discord but Discord never reaches the game | The message content intent is off. Go back to step 3. |
| `Discord relay needs the aiohttp package` | Your Python environment is missing aiohttp, which normally ships with Endstone. Reinstall Endstone. |

### Discord settings

These live in the `[discord]` section of `config.toml`. Secrets stay in `.env` and never go in `config.toml`.

| Key | Default | Meaning |
| --- | --- | --- |
| `enabled` | `true` | Master switch. Set to `false` to skip the module even when a token is present. |
| `relayChat` | `true` | Send player chat to Discord. |
| `relayDeaths` | `true` | Send death messages to Discord. |
| `relayJoinLeave` | `true` | Send join and leave messages to Discord. |
| `relayServerState` | `true` | Send server start and shutdown notices. |
| `sendIntervalSeconds` | `1.5` | How often queued lines are posted, batched into one message. |
| `inboundPollTicks` | `10` | How often Discord messages are handed to the game thread. Ten ticks is twice a second. |
| `maxInboundLength` | `256` | Longer Discord messages are cut short before being shown in game. |
| `chatFormat` | `**{name}**: {message}` | Layout of a relayed chat line. Discord markdown works here. |
| `eventFormat` | `_{message}_` | Layout of deaths, joins, leaves and server notices. |
| `inboundFormat` | `&9[Discord] &b{name}&7: &f{message}` | Layout of a Discord message shown in game. Supports `&` colour codes. |

### How the relay stays out of the way

The relay never runs on the server thread. Endstone ships a shared background event loop, and UtilityStone puts
its Discord work there through `endstone.asyncio`. Game events append a line to a bounded queue, which is all
the server thread ever does. The loop drains that queue on a timer and posts one batched message rather than
one request per chat line, which keeps a busy server well inside Discord's rate limits. Messages coming the
other way land in a second bounded queue and are read back on the server thread by a scheduled task, because
the Endstone API must only be touched from that thread.

Both queues have a fixed maximum size, so a Discord outage or a rate limit cannot grow memory without bound.
Mentions are disabled on every relayed message, so nobody can ping `@everyone` from in game, and colour codes
are stripped before a line leaves the server.

## How it stays fast with fifty players

These are the decisions that matter when a server is full.

**No per tick or per movement event handlers.** The usual cause of lag in an essentials plugin is a
`PlayerMoveEvent` listener, which fires many times per second for every player. With fifty players that is
thousands of Python calls a second. UtilityStone registers no movement listener at all. Teleport warmups and
AFK detection sample positions on a timer instead, twice a second and once every five seconds respectively.
The cost does not change with how fast players are moving.

**Cheap guard clauses on hot events.** The only genuinely hot event listened to is `ActorDamageEvent`, needed
for god mode. Its first line checks whether the god mode set is empty and returns immediately if it is, which
is the case on almost every server almost all of the time. No lookups, no allocation.

**Disk writes never touch the server thread.** All persistent data lives in memory. Writes set a dirty flag,
and a single background thread serialises and writes changed files on the save interval. Serialising holds a
lock for the microseconds it takes and the file write happens outside it. Files are written to a temporary
path and then moved into place, so a crash mid write cannot corrupt them. A file that is damaged anyway gets
renamed out of the way at load and rebuilt rather than taking the plugin down.

**Constant time lookups.** Sessions are held in dictionaries keyed by player UUID. Ignore lists are cached as
sets while a player is online instead of scanning stored lists. Teleport requests are indexed by both sender
and receiver, so accepting, denying and cleaning up on disconnect are all direct lookups.

**Small objects.** `PlayerSession` and the teleport records use `__slots__`. With fifty sessions plus pending
requests that saves a real amount of memory and makes attribute access faster.

**Bounded work.** The teleport timer only walks the requests and warmups that actually exist, which is usually
zero. Back history is capped per player. Playtime is written on a slow timer, not on every event.

**Failures stay contained.** Every command runs inside the router's error handler, so a bad argument or an
unexpected API result logs a traceback and tells the player something went wrong instead of bubbling up into
the server tick.

## Project layout

```
UtilityStone/
  pyproject.toml
  LICENSE
  README.md
  CHANGELOG.md
  src/endstone_utilitystone/
    __init__.py
    plugin.py            plugin class, command table, permission table
    config.toml          default config copied to the data folder on first run
    core/
      messages.py        prefixed and coloured replies
      router.py          command name to handler dispatch with error trapping
      sessions.py        per player in memory state
      settings.py        typed, clamped view over config.toml
      storage.py         json stores and the background writer
    services/
      afk.py             away detection and tagging
      homes.py           home storage and limits
      kits.py            kit definitions, cooldowns, item building
      profiles.py        persistent player records, playtime, ignore lists
      punishments.py     mutes, plus bans through the server ban list
      spawns.py          spawn point
      teleports.py       requests, warmups, cooldowns, back history
      warps.py           warp storage and access
    commands/
      base.py            shared helpers for command groups
      homes.py warps.py spawn.py teleports.py state.py
      messaging.py moderation.py kits.py info.py
    listeners/
      chat.py            chat delivery, mutes, ignore filtering
      connection.py      join and quit handling
      protection.py      god mode and death tracking
    integrations/
      discord/
        bridge.py        queues, lifecycle and thread handover
        env.py           minimal .env reader
        gateway.py       Discord websocket client
        rest.py          Discord http client
    util/
      durations.py       duration parsing and formatting
      locations.py       location encoding and distance
      text.py            colour codes and small string helpers
```

Data files are written to `plugins/utilitystone/`: `profiles.json`, `homes.json`, `warps.json`, `spawn.json`,
`punishments.json` and `kits.json`. The optional `.env` for the Discord relay goes in the same folder. Keep it
out of version control, it holds your bot token.

## Licence

MIT. See [LICENSE](LICENSE). Copy it, change it, ship it in your own project. Just keep the copyright notice
and credit Ozz as the original author.

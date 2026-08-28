# Changelog

All notable changes to UtilityStone are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-08-28

Fixes found by running the plugin on a real Endstone server. Anyone on 1.0.0 should upgrade, because none of
the event driven features worked on that release.

### Fixed

- Event handlers were never registered. The listener modules used `from __future__ import annotations`, which
  turns every annotation into a string, and the Endstone plugin loader requires a real class object. All six
  handlers were rejected at startup while the plugin still reported itself as ready. This broke join and quit
  handling, chat delivery, mutes, ignore filtering, god mode, death tracking for `/back`, and the whole
  Discord relay.
- The Discord relay user agent pointed at a repository that does not exist and carried a stale version.

### Removed

- `/ban` and `/unban`. Bedrock already registers both, so the plugin could not claim the names. `/tempban`
  covers timed bans and accepts `perm` for a permanent ban with a reason. Every ban still goes through the
  server ban list, so vanilla `/unban` lifts them. The command count is now 40.

## [1.0.0] - 2026-08-28

First release. Built against Endstone 0.11.9 and Minecraft Bedrock 26.44.

### Added

- Homes with per permission limits: `/sethome`, `/home`, `/delhome`, `/homes`.
- Warps with optional per warp permissions: `/warp`, `/warps`, `/setwarp`, `/delwarp`.
- Spawn point handling and an optional first join teleport: `/spawn`, `/setspawn`.
- Teleport requests with warmup, cooldown and expiry: `/tpa`, `/tpahere`, `/tpaccept`, `/tpdeny`, `/tpcancel`.
- Return travel through `/back`, including a death location.
- Player state commands: `/heal`, `/feed`, `/fly`, `/god`, `/speed`, `/repair`.
- Private messaging and ignore lists: `/pm`, `/reply`, `/ignore`, `/unignore`, `/ignorelist`, `/broadcast`.
- Moderation: `/ban`, `/tempban`, `/unban`, `/mute`, `/unmute`, with duration parsing such as `1d12h` and `perm`.
- Configurable kits with cooldowns, custom names, lore and enchantments: `/kit`, `/kits`.
- Information commands: `/who`, `/ping`, `/playtime`, `/seen`, `/whois`, `/afk`.
- Plugin control through `/utilitystone info` and `/utilitystone reload`.
- Automatic AFK detection driven by position sampling rather than movement events.
- Managed chat delivery so that `/ignore` works on public chat, switchable through `chat.manageFormat`.
- Background storage writer with dirty tracking, atomic file replacement and recovery from damaged files.
- Optional two way Discord relay. Player chat, death messages, join and leave notices and server state go to a
  Discord channel, and messages posted in that channel are shown in game.
- Discord credentials are read from a `.env` file in the plugin folder, the server folder or the real
  environment. The relay stays off and the plugin runs normally when nothing is configured.
- Discord work runs on the Endstone background event loop with bounded queues, batched sending and mentions
  disabled, so the server thread never waits on the network.

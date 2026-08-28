from endstone_utilitystone.commands.base import CommandGroup
from endstone_utilitystone.commands.homes import HomeCommands
from endstone_utilitystone.commands.info import InfoCommands
from endstone_utilitystone.commands.kits import KitCommands
from endstone_utilitystone.commands.messaging import MessagingCommands
from endstone_utilitystone.commands.moderation import ModerationCommands
from endstone_utilitystone.commands.spawn import SpawnCommands
from endstone_utilitystone.commands.state import StateCommands
from endstone_utilitystone.commands.teleports import TeleportCommands
from endstone_utilitystone.commands.warps import WarpCommands

COMMAND_GROUPS = (
    HomeCommands,
    WarpCommands,
    SpawnCommands,
    TeleportCommands,
    StateCommands,
    MessagingCommands,
    ModerationCommands,
    KitCommands,
    InfoCommands,
)

__all__ = [
    "COMMAND_GROUPS",
    "CommandGroup",
    "HomeCommands",
    "InfoCommands",
    "KitCommands",
    "MessagingCommands",
    "ModerationCommands",
    "SpawnCommands",
    "StateCommands",
    "TeleportCommands",
    "WarpCommands",
]

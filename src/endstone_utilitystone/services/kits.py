from __future__ import annotations

import time

from endstone.inventory import ItemStack

from endstone_utilitystone.util.text import colorize


def buildItem(entry) -> ItemStack | None:
    if isinstance(entry, str):
        pieces = entry.split()
        entry = {"type": pieces[0], "amount": pieces[1] if len(pieces) > 1 else 1}

    if not isinstance(entry, dict):
        return None

    itemType = str(entry.get("type", "")).strip()
    if not itemType:
        return None

    try:
        amount = max(1, min(255, int(entry.get("amount", 1))))
    except (TypeError, ValueError):
        amount = 1

    try:
        stack = ItemStack(itemType, amount)
    except Exception:
        return None

    meta = stack.item_meta
    touched = False

    displayName = entry.get("name")
    if displayName:
        meta.display_name = colorize(str(displayName))
        touched = True

    lore = entry.get("lore")
    if isinstance(lore, (list, tuple)) and lore:
        meta.lore = [colorize(str(line)) for line in lore]
        touched = True

    enchants = entry.get("enchants")
    if isinstance(enchants, dict):
        for enchantId, level in enchants.items():
            try:
                if meta.add_enchant(str(enchantId), int(level), True):
                    touched = True
            except Exception:
                continue

    if touched:
        stack.set_item_meta(meta)

    return stack


class KitService:
    def __init__(self, plugin):
        self.plugin = plugin
        self.store = plugin.storage.open("kits", {})

    def availableTo(self, player) -> list:
        names = []
        for name in self.plugin.settings.kitNames():
            definition = self.plugin.settings.kitDefinition(name)
            if definition is None:
                continue
            if self.canUse(player, name, definition):
                names.append(name)
        return names

    def permissionFor(self, name: str, definition: dict) -> str | None:
        declared = definition.get("permission")
        return str(declared) if declared else None

    def canUse(self, player, name: str, definition: dict) -> bool:
        node = self.permissionFor(name, definition)
        if node is None:
            return True
        return player.has_permission(node)

    def cooldownRemaining(self, player, name: str, definition: dict) -> float:
        cooldown = self.plugin.settings.kitCooldownSeconds(definition)
        if cooldown <= 0.0:
            return 0.0

        owned = self.store.data.get(str(player.unique_id))
        if not owned:
            return 0.0

        lastUsed = owned.get(name)
        if lastUsed is None:
            return 0.0

        remaining = (float(lastUsed) + cooldown) - time.time()
        return remaining if remaining > 0.0 else 0.0

    def markUsed(self, player, name: str) -> None:
        owned = self.store.data.setdefault(str(player.unique_id), {})
        owned[name] = time.time()
        self.store.markDirty()

    def grant(self, player, name: str, definition: dict) -> tuple:
        rawItems = definition.get("items")
        if not isinstance(rawItems, (list, tuple)) or not rawItems:
            return False, 0, 0

        stacks = []
        rejected = 0
        for entry in rawItems:
            stack = buildItem(entry)
            if stack is None:
                rejected += 1
                continue
            stacks.append(stack)

        if not stacks:
            return False, 0, rejected

        leftovers = player.inventory.add_item(*stacks)
        if leftovers:
            dimension = player.location.dimension
            for stack in leftovers.values():
                dimension.drop_item(player.location, stack)

        return True, len(stacks), rejected

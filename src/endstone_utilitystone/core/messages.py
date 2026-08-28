from __future__ import annotations

from endstone import ColorFormat

from endstone_utilitystone.util.text import colorize


class Messages:
    def __init__(self, settings):
        self.settings = settings

    def prefixed(self, body: str) -> str:
        if not self.settings.usePrefix:
            return body
        return colorize(self.settings.prefix) + body

    def info(self, sender, text: str) -> None:
        sender.send_message(self.prefixed(ColorFormat.GRAY + colorize(text)))

    def success(self, sender, text: str) -> None:
        sender.send_message(self.prefixed(ColorFormat.GREEN + colorize(text)))

    def notice(self, sender, text: str) -> None:
        sender.send_message(self.prefixed(ColorFormat.AQUA + colorize(text)))

    def warn(self, sender, text: str) -> None:
        sender.send_message(self.prefixed(ColorFormat.YELLOW + colorize(text)))

    def failure(self, sender, text: str) -> None:
        sender.send_error_message(self.prefixed(ColorFormat.RED + colorize(text)))

    def heading(self, sender, text: str) -> None:
        sender.send_message(ColorFormat.DARK_AQUA + ColorFormat.BOLD + colorize(text))

    def listing(self, sender, label: str, value: str) -> None:
        sender.send_message(f"{ColorFormat.GRAY}{label}: {ColorFormat.WHITE}{colorize(value)}")

    def raw(self, sender, text: str) -> None:
        sender.send_message(colorize(text))

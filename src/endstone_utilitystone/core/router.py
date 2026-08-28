from __future__ import annotations

import traceback


class CommandRouter:
    def __init__(self, logger):
        self.logger = logger
        self._routes: dict = {}

    def add(self, group) -> None:
        for name, handler in group.bindings().items():
            self._routes[name] = handler

    def dispatch(self, sender, name: str, args: list) -> bool:
        handler = self._routes.get(name)
        if handler is None:
            return False

        try:
            return handler(sender, args)
        except Exception:
            self.logger.error(f"The command '{name}' failed:\n{traceback.format_exc()}")
            sender.send_error_message("That command ran into a problem. The console has the details.")
            return True

    @property
    def count(self) -> int:
        return len(self._routes)

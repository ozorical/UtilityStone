from __future__ import annotations

import json
import os
import threading
import time
import traceback
from pathlib import Path


class StoreLoadError(Exception):
    def __init__(self, path: Path, cause: Exception):
        super().__init__(f"{path.name}: {cause}")
        self.path = path
        self.cause = cause


class JsonStore:
    def __init__(self, path: Path, fallback: dict | None = None):
        self.path = path
        self.data: dict = dict(fallback) if fallback else {}
        self._lock = threading.RLock()
        self._dirty = False

    def load(self) -> None:
        if not self.path.exists():
            self._dirty = True
            return

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (OSError, ValueError) as error:
            raise StoreLoadError(self.path, error) from error

        if not isinstance(loaded, dict):
            raise StoreLoadError(self.path, TypeError("root value is not an object"))

        with self._lock:
            self.data.update(loaded)

    def markDirty(self) -> None:
        with self._lock:
            self._dirty = True

    def takeSnapshot(self) -> str | None:
        with self._lock:
            if not self._dirty:
                return None
            self._dirty = False
            return json.dumps(self.data, separators=(",", ":"))

    def writeSnapshot(self, payload: str) -> None:
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.parent.mkdir(parents=True, exist_ok=True)

        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary, self.path)

    def quarantine(self) -> Path | None:
        if not self.path.exists():
            return None

        target = self.path.with_name(f"{self.path.name}.broken.{int(time.time())}")
        try:
            os.replace(self.path, target)
        except OSError:
            return None
        return target


class StorageManager:
    def __init__(self, folder, logger, intervalSeconds: float = 30.0):
        self.folder = Path(folder)
        self.logger = logger
        self.intervalSeconds = min(900.0, max(5.0, float(intervalSeconds)))
        self._stores: dict[str, JsonStore] = {}
        self._stopSignal = threading.Event()
        self._worker: threading.Thread | None = None

    def open(self, name: str, fallback: dict | None = None) -> JsonStore:
        existing = self._stores.get(name)
        if existing is not None:
            return existing

        store = JsonStore(self.folder / f"{name}.json", fallback)
        try:
            store.load()
        except StoreLoadError as error:
            moved = store.quarantine()
            self.logger.error(f"Could not read {name}.json: {error.cause}")
            if moved is not None:
                self.logger.error(f"The damaged file was renamed to {moved.name}, a fresh one will be created.")
            store.markDirty()

        self._stores[name] = store
        return store

    def start(self) -> None:
        if self._worker is not None:
            return

        self._stopSignal.clear()
        self._worker = threading.Thread(target=self._runFlushLoop, name="UtilityStoneStorage", daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stopSignal.set()
        worker = self._worker
        self._worker = None

        if worker is not None:
            worker.join(timeout=10.0)

        self.flushAll()

    def flushAll(self) -> int:
        written = 0
        for store in list(self._stores.values()):
            payload = store.takeSnapshot()
            if payload is None:
                continue

            try:
                store.writeSnapshot(payload)
                written += 1
            except OSError as error:
                store.markDirty()
                self.logger.error(f"Could not save {store.path.name}: {error}")

        return written

    def _runFlushLoop(self) -> None:
        while not self._stopSignal.wait(self.intervalSeconds):
            try:
                self.flushAll()
            except Exception:
                self.logger.error(f"Background save failed:\n{traceback.format_exc()}")

from threading import Lock
from typing import Literal

IDLE = "idle"
RENDERING = "rendering"
DONE = "done"
ERROR = "error"


class AtomicStatusContainer:
    def __init__(self):
        self._is_rendering: bool = False
        self._status: Literal["idle", "rendering", "done", "error"] = IDLE
        self._log: str = ""
        self._lock: Lock = Lock()

    def start_render(self):
        with self._lock:
            self._is_rendering = True

    def set_status(self, status: Literal["idle", "rendering", "done", "error"]):
        with self._lock:
            self._status = status

    def add_log(self, log: str):
        with self._lock:
            self._log += f"\n{log}"

    def get_status(self):
        with self._lock:
            return self._status

    def reset(self):
        with self._lock:
            self._is_rendering = False
            self._status = IDLE
            self._log = ""

    def get_all(self):
        with self._lock:
            all = {
                "is_rendering": self._is_rendering,
                "status": self._status,
                "log": self._log,
            }
        return all

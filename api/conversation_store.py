from __future__ import annotations

from copy import deepcopy
from threading import Lock


Message = dict[str, str]


class ConversationStore:
    """In-memory chat history keyed by browser session."""

    def __init__(self) -> None:
        self._histories: dict[str, list[Message]] = {}
        self._lock = Lock()

    def get_history(self, session_id: str) -> list[Message]:
        with self._lock:
            return deepcopy(self._histories.get(session_id, []))

    def add_exchange(self, session_id: str, user_content: str, assistant_content: str) -> list[Message]:
        with self._lock:
            history = self._histories.setdefault(session_id, [])
            history.append({"role": "user", "content": user_content})
            history.append({"role": "assistant", "content": assistant_content})
            return deepcopy(history)

    def clear(self, session_id: str | None = None) -> None:
        with self._lock:
            if session_id:
                self._histories.pop(session_id, None)
                return
            self._histories.clear()

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class EventLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: str, **payload: Any) -> None:
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "event": event,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

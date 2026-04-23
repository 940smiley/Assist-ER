from __future__ import annotations

import webbrowser
from pathlib import Path


def launch_gui() -> str:
    index = Path("gui/src/index.html").resolve()
    webbrowser.open(index.as_uri())
    return str(index)

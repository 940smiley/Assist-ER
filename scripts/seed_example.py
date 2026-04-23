"""Generate sample payloads for local API and CLI testing."""

from pathlib import Path

import json

example = {
    "repository": {"owner": "octocat", "name": "hello-world", "enabled": True, "control_mode": "limited"},
    "branch_name": "assist-er/seed-example",
    "file_updates": {
        "docs/assist-er-note.md": "# Managed by Assist-ER\\n\\nThis file was generated as a seed example.\\n"
    },
}

Path(".assist-er").mkdir(exist_ok=True)
Path(".assist-er/example-batch-edit.json").write_text(json.dumps(example, indent=2), encoding="utf-8")
print("Wrote .assist-er/example-batch-edit.json")

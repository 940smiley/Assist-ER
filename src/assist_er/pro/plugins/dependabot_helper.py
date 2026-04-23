from __future__ import annotations

import base64
from pathlib import Path

from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.models import DependencyUpdateResult, RepoRef


class DependabotHelper:
    def __init__(self, rest_client: RestClient) -> None:
        self.rest = rest_client

    def ensure_config(self, repo: RepoRef) -> DependencyUpdateResult:
        config_path = Path(__file__).resolve().parents[1] / "templates" / "dependabot.yml"
        content = config_path.read_text(encoding="utf-8")
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        target = ".github/dependabot.yml"
        self.rest.request(
            "PUT",
            f"/repos/{repo.slug}/contents/{target}",
            json={
                "message": "assist-er pro: ensure dependabot config",
                "content": encoded,
                "branch": repo.default_branch,
            },
        )
        return DependencyUpdateResult(
            repo=repo.slug,
            updated_files=[target],
            created_branch=repo.default_branch,
            success=True,
        )

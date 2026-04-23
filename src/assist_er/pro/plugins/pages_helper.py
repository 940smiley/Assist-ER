from __future__ import annotations

import base64
from pathlib import Path

from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.models import PagesResult, RepoRef


class PagesHelper:
    def __init__(self, rest_client: RestClient) -> None:
        self.rest = rest_client

    def setup_pages(self, repo: RepoRef) -> PagesResult:
        index_template = Path(__file__).resolve().parents[1] / "templates" / "pages_index.html"
        content = index_template.read_text(encoding="utf-8")
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        self.rest.request(
            "PUT",
            f"/repos/{repo.slug}/contents/docs/index.html",
            json={
                "message": "assist-er pro: scaffold pages",
                "content": encoded,
                "branch": repo.default_branch,
            },
        )
        self.rest.request(
            "POST",
            f"/repos/{repo.slug}/pages",
            json={"source": {"branch": repo.default_branch, "path": "/docs"}},
        )
        return PagesResult(repo=repo.slug, action="setup", success=True)

    def repair_pages(self, repo: RepoRef) -> PagesResult:
        page_info = self.rest.request("GET", f"/repos/{repo.slug}/pages")
        build_status = page_info.get("status", "unknown")
        if build_status != "built":
            self.rest.request("POST", f"/repos/{repo.slug}/pages/builds")
        return PagesResult(
            repo=repo.slug,
            action="repair",
            success=True,
            details={"status": build_status},
        )

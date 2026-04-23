from __future__ import annotations

import base64
from pathlib import Path

from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.models import RepoRef, WorkflowAuditResult


class WorkflowManager:
    def __init__(self, rest_client: RestClient) -> None:
        self.rest = rest_client

    def audit(self, repo: RepoRef) -> WorkflowAuditResult:
        workflows = self.rest.request("GET", f"/repos/{repo.slug}/actions/workflows")
        names = {w["name"].lower() for w in workflows.get("workflows", [])}
        has_ci = any("ci" in n or "test" in n for n in names)
        has_dependabot = "dependabot" in names
        recommendations: list[str] = []
        if not has_ci:
            recommendations.append("Add CI workflow with lint/test checks")
        if not has_dependabot:
            recommendations.append("Enable Dependabot workflow or config")
        return WorkflowAuditResult(
            repo=repo.slug,
            has_ci=has_ci,
            has_dependabot=has_dependabot,
            recommendations=recommendations,
        )

    def apply_template(
        self,
        repo: RepoRef,
        template_name: str = "pro_maintenance.yml",
    ) -> dict[str, str]:
        template = Path(__file__).resolve().parents[2] / "templates" / template_name
        content = template.read_text(encoding="utf-8")
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        path = ".github/workflows/assist-er-pro.yml"

        sha = None
        try:
            existing = self.rest.request("GET", f"/repos/{repo.slug}/contents/{path}")
            sha = existing.get("sha")
        except Exception:
            sha = None

        payload: dict[str, str] = {
            "message": "assist-er pro: apply workflow template",
            "content": encoded,
            "branch": repo.default_branch,
        }
        if sha:
            payload["sha"] = sha

        self.rest.request("PUT", f"/repos/{repo.slug}/contents/{path}", json=payload)
        return {"path": path, "status": "updated"}

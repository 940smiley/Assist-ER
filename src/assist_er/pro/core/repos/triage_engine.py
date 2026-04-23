from __future__ import annotations

from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.models import RepoRef, RepoTriageResult


class RepoTriageEngine:
    def __init__(self, rest_client: RestClient) -> None:
        self.rest = rest_client

    def triage(self, repo: RepoRef) -> RepoTriageResult:
        issues = self.rest.request(
            "GET",
            f"/repos/{repo.slug}/issues",
            params={"state": "open", "per_page": 100},
        )
        pulls = self.rest.request(
            "GET",
            f"/repos/{repo.slug}/pulls",
            params={"state": "open", "per_page": 100},
        )
        issue_count = sum(1 for i in issues if "pull_request" not in i)
        pr_count = len(pulls)
        severity = (issue_count * 2) + (pr_count * 3)
        findings: list[str] = []
        if issue_count > 20:
            findings.append("High issue volume detected")
        if pr_count > 10:
            findings.append("PR backlog exceeds threshold")
        return RepoTriageResult(
            repo=repo.slug,
            open_issues=issue_count,
            open_prs=pr_count,
            severity_score=severity,
            findings=findings,
        )

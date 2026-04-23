from __future__ import annotations

from assist_er.pro.core.ai.conflict_resolver import ConflictResolver
from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.models import PullRequestRecord, PullRequestState, RepoRef


class PullRequestManager:
    def __init__(self, rest_client: RestClient, resolver: ConflictResolver | None = None) -> None:
        self.rest = rest_client
        self.resolver = resolver or ConflictResolver()

    def list_prs(self, repo: RepoRef) -> list[PullRequestRecord]:
        prs = self.rest.request(
            "GET",
            f"/repos/{repo.slug}/pulls",
            params={"state": "open", "per_page": 100},
        )
        results: list[PullRequestRecord] = []
        for pr in prs:
            results.append(
                PullRequestRecord(
                    number=pr["number"],
                    title=pr["title"],
                    state=PullRequestState.open,
                    draft=pr.get("draft", False),
                    mergeable_state=pr.get("mergeable_state"),
                    labels=[label["name"] for label in pr.get("labels", [])],
                )
            )
        return results

    def merge_pr(
        self,
        repo: RepoRef,
        number: int,
        merge_method: str = "squash",
    ) -> dict[str, str | bool]:
        response = self.rest.request(
            "PUT",
            f"/repos/{repo.slug}/pulls/{number}/merge",
            json={"merge_method": merge_method},
        )
        return {"merged": bool(response.get("merged")), "message": str(response.get("message", ""))}

    def close_pr(self, repo: RepoRef, number: int) -> dict[str, str]:
        response = self.rest.request(
            "PATCH",
            f"/repos/{repo.slug}/pulls/{number}",
            json={"state": "closed"},
        )
        return {"state": str(response.get("state", "closed"))}

    def resolve_check_merge(self, repo: RepoRef, number: int) -> dict[str, str | bool]:
        pr = self.rest.request("GET", f"/repos/{repo.slug}/pulls/{number}")
        mergeable_state = pr.get("mergeable_state", "unknown")
        if mergeable_state == "dirty":
            resolution_note = self.resolver.resolve(repo.slug, number)
            return {"resolved": False, "message": resolution_note}
        if mergeable_state in {"clean", "unstable", "has_hooks", None}:
            return self.merge_pr(repo, number)
        return {"resolved": False, "message": f"Cannot auto-merge state: {mergeable_state}"}

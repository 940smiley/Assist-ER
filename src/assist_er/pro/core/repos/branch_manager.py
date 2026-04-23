from __future__ import annotations

from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.models import BranchActionResult, RepoRef


class BranchManager:
    def __init__(self, rest_client: RestClient) -> None:
        self.rest = rest_client

    def create_branch(
        self,
        repo: RepoRef,
        branch_name: str,
        from_branch: str | None = None,
    ) -> BranchActionResult:
        source = from_branch or repo.default_branch
        base = self.rest.request("GET", f"/repos/{repo.slug}/git/ref/heads/{source}")
        sha = base["object"]["sha"]
        self.rest.request(
            "POST",
            f"/repos/{repo.slug}/git/refs",
            json={"ref": f"refs/heads/{branch_name}", "sha": sha},
        )
        return BranchActionResult(
            success=True,
            branch=branch_name,
            action="create",
            message="Branch created",
        )

    def delete_branch(self, repo: RepoRef, branch_name: str) -> BranchActionResult:
        self.rest.request("DELETE", f"/repos/{repo.slug}/git/refs/heads/{branch_name}")
        return BranchActionResult(
            success=True,
            branch=branch_name,
            action="delete",
            message="Branch deleted",
        )

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from assist_er.config import settings
from assist_er.models import Issue, PullRequest, RepositoryAccess

logger = logging.getLogger(__name__)


class GitHubAPIError(RuntimeError):
    """Raised when GitHub API request fails."""


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._token = token or settings.github_token
        self._base_url = (base_url or settings.github_api_url).rstrip("/")
        self._timeout = timeout or settings.request_timeout_seconds
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        self._client = httpx.Client(base_url=self._base_url, headers=headers, timeout=self._timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @retry(
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        logger.debug("GitHub %s %s", method, endpoint)
        response = self._client.request(method, endpoint, **kwargs)
        if response.status_code >= 400:
            raise GitHubAPIError(f"GitHub API error {response.status_code}: {response.text}")
        return response.json() if response.text else {}

    def list_user_repositories(self) -> list[RepositoryAccess]:
        data = self._request("GET", "/user/repos", params={"per_page": 100, "sort": "updated"})
        return [
            RepositoryAccess(owner=item["owner"]["login"], name=item["name"], enabled=True)
            for item in data
        ]

    def list_open_pull_requests(self, repo: RepositoryAccess) -> list[PullRequest]:
        data = self._request(
            "GET",
            f"/repos/{repo.slug}/pulls",
            params={"state": "open", "per_page": 100},
        )
        return [
            PullRequest(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                mergeable_state=item.get("mergeable_state"),
                draft=item.get("draft", False),
                labels=[label["name"] for label in item.get("labels", [])],
                html_url=item["html_url"],
            )
            for item in data
        ]

    def list_open_issues(self, repo: RepositoryAccess) -> list[Issue]:
        data = self._request(
            "GET",
            f"/repos/{repo.slug}/issues",
            params={"state": "open", "per_page": 100},
        )
        issues: list[Issue] = []
        for item in data:
            if "pull_request" in item:
                continue
            issues.append(
                Issue(
                    number=item["number"],
                    title=item["title"],
                    state=item["state"],
                    labels=[label["name"] for label in item.get("labels", [])],
                    body=item.get("body") or "",
                    html_url=item["html_url"],
                )
            )
        return issues

    def add_labels(self, repo: RepositoryAccess, issue_number: int, labels: list[str]) -> None:
        self._request(
            "POST",
            f"/repos/{repo.slug}/issues/{issue_number}/labels",
            json={"labels": labels},
        )

    def merge_pull_request(
        self,
        repo: RepositoryAccess,
        pr_number: int,
        merge_method: str = "squash",
    ) -> dict[str, Any]:
        response = self._request(
            "PUT",
            f"/repos/{repo.slug}/pulls/{pr_number}/merge",
            json={"merge_method": merge_method},
        )
        return dict(response)

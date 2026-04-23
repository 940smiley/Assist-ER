from __future__ import annotations

from assist_er.pro.core.api.pagination import paginate
from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.models import RepoRef


class RepositoryManager:
    def __init__(self, rest_client: RestClient) -> None:
        self.rest = rest_client

    def list_accessible_repositories(self) -> list[RepoRef]:
        repos: list[RepoRef] = []
        for item in paginate(
            self.rest,
            "/user/repos",
            params={"affiliation": "owner,collaborator,organization_member"},
        ):
            repos.append(
                RepoRef(
                    owner=item["owner"]["login"],
                    name=item["name"],
                    default_branch=item.get("default_branch") or "main",
                )
            )
        return repos

    def select_repositories(self, names: list[str]) -> list[RepoRef]:
        selected: list[RepoRef] = []
        lookup = set(names)
        for repo in self.list_accessible_repositories():
            if repo.slug in lookup:
                selected.append(repo)
        return selected

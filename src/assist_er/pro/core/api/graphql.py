from __future__ import annotations

from typing import Any, cast

from assist_er.pro.core.api.rest import RestClient


class GraphQLClient:
    def __init__(self, rest_client: RestClient) -> None:
        self.rest_client = rest_client

    def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        response = self.rest_client.request("POST", "/graphql", json=payload)
        if "errors" in response:
            raise RuntimeError(f"GraphQL errors: {response['errors']}")
        return cast(dict[str, Any], response.get("data", {}))

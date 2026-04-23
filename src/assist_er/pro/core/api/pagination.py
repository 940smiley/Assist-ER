from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from assist_er.pro.core.api.rest import RestClient


def paginate(
    rest_client: RestClient,
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    page = 1
    while True:
        payload = rest_client.request(
            "GET",
            endpoint,
            params={**(params or {}), "per_page": 100, "page": page},
        )
        if not payload:
            break
        yield from payload
        if len(payload) < 100:
            break
        page += 1

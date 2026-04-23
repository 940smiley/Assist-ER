from __future__ import annotations

from typing import Any

import httpx


class RestClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
        timeout: float = 20.0,
    ) -> None:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.client = httpx.Client(base_url=base_url.rstrip("/"), headers=headers, timeout=timeout)

    def request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        response = self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        if not response.text:
            return {}
        return response.json()

    def close(self) -> None:
        self.client.close()

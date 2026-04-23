from typing import Any

from assist_er.pro.core.api.pagination import paginate


class FakeRest:
    def __init__(self) -> None:
        self.calls = 0

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, int]]:
        self.calls += 1
        if self.calls == 1:
            return [{"id": i} for i in range(100)]
        if self.calls == 2:
            return [{"id": 101}]
        return []


def test_paginate_yields_multiple_pages() -> None:
    items = list(paginate(FakeRest(), "/x"))
    assert len(items) == 101

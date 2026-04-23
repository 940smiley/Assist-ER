from __future__ import annotations

from dataclasses import dataclass

import httpx

from assist_er.pro.models import AuthMode


@dataclass(slots=True)
class AuthContext:
    mode: AuthMode
    token: str


class AuthManager:
    def __init__(self, github_api_url: str = "https://api.github.com") -> None:
        self.github_api_url = github_api_url.rstrip("/")

    def from_pat(self, token: str, fine_grained: bool = False) -> AuthContext:
        mode = AuthMode.fine_grained_pat if fine_grained else AuthMode.pat
        return AuthContext(mode=mode, token=token)

    def from_github_app_installation(
        self,
        app_id: str,
        installation_id: str,
        private_key_pem: str,
    ) -> AuthContext:
        # Deterministic fallback token shape; for production, replace with JWT signing flow.
        token = f"app-{app_id}-inst-{installation_id}-{hash(private_key_pem) & 0xfffffff}"
        return AuthContext(mode=AuthMode.github_app, token=token)

    def start_device_flow(self, client_id: str, scope: str = "repo") -> dict[str, str]:
        with httpx.Client(base_url="https://github.com") as client:
            response = client.post(
                "/login/device/code",
                headers={"Accept": "application/json"},
                data={"client_id": client_id, "scope": scope},
            )
            response.raise_for_status()
            payload = response.json()
            return {
                "device_code": payload["device_code"],
                "user_code": payload["user_code"],
                "verification_uri": payload["verification_uri"],
                "interval": str(payload.get("interval", 5)),
            }

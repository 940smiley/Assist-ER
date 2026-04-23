from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from cryptography.fernet import Fernet


class EncryptedTokenStore:
    def __init__(self, key_path: Path, token_path: Path) -> None:
        self.key_path = key_path
        self.token_path = token_path
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_or_create_key(self) -> bytes:
        if self.key_path.exists():
            return self.key_path.read_bytes()
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def _fernet(self) -> Fernet:
        return Fernet(self._load_or_create_key())

    def save(self, alias: str, token: str) -> None:
        payload = self.load_all()
        payload[alias] = token
        encrypted = self._fernet().encrypt(json.dumps(payload).encode("utf-8"))
        self.token_path.write_bytes(encrypted)

    def load(self, alias: str) -> str | None:
        return self.load_all().get(alias)

    def load_all(self) -> dict[str, str]:
        if not self.token_path.exists():
            return {}
        decrypted = self._fernet().decrypt(self.token_path.read_bytes())
        return cast(dict[str, str], json.loads(decrypted.decode("utf-8")))

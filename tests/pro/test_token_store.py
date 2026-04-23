from pathlib import Path

from assist_er.pro.core.auth.token_store import EncryptedTokenStore


def test_encrypted_token_store_roundtrip(tmp_path: Path) -> None:
    store = EncryptedTokenStore(tmp_path / "key.bin", tmp_path / "tokens.enc")
    store.save("default", "abc123")
    assert store.load("default") == "abc123"

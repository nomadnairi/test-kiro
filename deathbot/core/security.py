"""Cryptography helpers — AES-256-GCM authenticated encryption.

Used to encrypt per-user provider API keys at rest. The master key is derived
from ``SECRET_KEY`` (env) or persisted to a local key file on first run.
"""
from __future__ import annotations

import base64
import binascii
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..logging_setup import get_logger

log = get_logger("security")
_NONCE_BYTES = 12
_KEY_BYTES = 32


def _coerce_key(raw: str) -> bytes | None:
    """Accept a 32-byte key as raw / hex / base64; return None if unusable."""
    if not raw:
        return None
    data = raw.encode()
    if len(data) == _KEY_BYTES:
        return data
    for decoder in (base64.b64decode, base64.urlsafe_b64decode, binascii.unhexlify):
        try:
            candidate = decoder(raw)
            if len(candidate) == _KEY_BYTES:
                return candidate
        except (binascii.Error, ValueError):
            continue
    return None


class Crypto:
    """AES-256-GCM wrapper. ``encrypt`` returns urlsafe-base64 ``nonce||ct``."""

    def __init__(self, key: bytes) -> None:
        if len(key) != _KEY_BYTES:
            raise ValueError("AES-256 key must be 32 bytes")
        self._aead = AESGCM(key)

    @classmethod
    def from_settings(cls, secret_key: str, key_file: str | Path = ".secret.key") -> "Crypto":
        key = _coerce_key(secret_key)
        if key is None:
            key = cls._load_or_create_key_file(Path(key_file))
        return cls(key)

    @staticmethod
    def _load_or_create_key_file(path: Path) -> bytes:
        if path.exists():
            return path.read_bytes()[:_KEY_BYTES].ljust(_KEY_BYTES, b"\0")
        key = AESGCM.generate_key(bit_length=256)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(key)
        except OSError as exc:
            raise SystemExit(
                f"Cannot write the encryption key to {path}: {exc}\n"
                "The bot needs a writable location for its state. In Docker this "
                "must point at the mounted volume — set SECRET_KEY_FILE and "
                "DATABASE_PATH to paths under /data (compose does this for you), "
                "or provide a ready-made 32-byte SECRET_KEY instead."
            ) from exc
        try:
            os.chmod(path, 0o600)
        except OSError:  # non-POSIX filesystems
            pass
        log.warning("Generated new master key at %s (keep it safe)", path)
        return key

    def encrypt(self, plaintext: str, aad: bytes = b"") -> str:
        nonce = os.urandom(_NONCE_BYTES)
        ct = self._aead.encrypt(nonce, plaintext.encode(), aad)
        return base64.urlsafe_b64encode(nonce + ct).decode()

    def decrypt(self, token: str, aad: bytes = b"") -> str:
        blob = base64.urlsafe_b64decode(token.encode())
        nonce, ct = blob[:_NONCE_BYTES], blob[_NONCE_BYTES:]
        return self._aead.decrypt(nonce, ct, aad).decode()

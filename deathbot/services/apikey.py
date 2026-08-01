"""ApiKeyService — stores per-user provider keys encrypted with AES-256-GCM."""
from __future__ import annotations

from ..core.security import Crypto
from ..repositories import Repositories


class ApiKeyService:
    def __init__(self, repos: Repositories, crypto: Crypto) -> None:
        self.repos = repos
        self.crypto = crypto

    async def set_key(self, user_id: int, provider: str, plaintext: str) -> None:
        # Bind the ciphertext to the user id (AAD) so it can't be transplanted.
        aad = f"{user_id}:{provider}".encode()
        ciphertext = self.crypto.encrypt(plaintext, aad=aad)
        await self.repos.api_keys.set(user_id, provider.lower(), ciphertext)
        await self.repos.audit.log(user_id, "apikey.set", provider)

    async def get_key(self, user_id: int, provider: str) -> str | None:
        ciphertext = await self.repos.api_keys.get(user_id, provider.lower())
        if ciphertext is None:
            return None
        aad = f"{user_id}:{provider}".encode()
        try:
            return self.crypto.decrypt(ciphertext, aad=aad)
        except Exception:  # noqa: BLE001 — corrupted / wrong key
            return None

    async def list_providers(self, user_id: int) -> list[str]:
        return await self.repos.api_keys.list_providers(user_id)

    async def delete(self, user_id: int, provider: str) -> None:
        await self.repos.api_keys.delete(user_id, provider.lower())
        await self.repos.audit.log(user_id, "apikey.delete", provider)

    async def delete_all(self, user_id: int) -> None:
        await self.repos.api_keys.delete_all(user_id)
        await self.repos.audit.log(user_id, "apikey.delete_all", "")

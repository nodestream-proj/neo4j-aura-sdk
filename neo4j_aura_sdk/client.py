import os
import time
from typing import Type

import httpx
from pydantic import BaseModel

from .models import AuthResponse, TenantsResponse


class AuraClient:
    """An API Client for the Neo4j Aura service.

    This client provides a low-ish level interface to the Neo4j Aura service.
    It is intended to be used by higher level libraries that provide a more
    user-friendly interface.

    This client is not thread-safe. If you need to use it in a multi-threaded
    environment, you should create a new client for each thread.

    Usage:

    ```python
    from neo4j_aura_sdk import AuraClient

    client_id = "..."
    client_secret = "..."

    async with AuraClient(client_id, client_secret) as client:
        # Do stuff with the client
    ```
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.neo4j.io",
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._token = None
        self._token_expiration = 0
        self._client = httpx.AsyncClient()

    @classmethod
    def from_env(cls):
        client_id = os.environ["AURA_API_CLIENT_TOKEN"]
        client_secret = os.environ["AURA_API_CLIENT_SECRET"]
        return cls(client_id, client_secret)

    # AsyncClient is a context manager, so we need to implement __aenter__ and
    # __aexit__ to make this class a context manager as well. This allows us to
    # use the `async with` syntax.

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)

    async def _get_token(self):
        # NOTE: This method is a bit complex because it handles token
        #       expiration. We could simplify it through refactoring or
        #       by using a custom authentication class.
        current_time = time.monotonic()
        if current_time < self._token_expiration:
            return self._token

        response = await self._client.post(
            f"{self._base_url}/oauth/token",
            data={"grant_type": "client_credentials"},
            auth=(self._client_id, self._client_secret),
        )

        # TODO: We should handle the case where the response is not a 200
        #       and throw a butter excpettion than just raising an error.
        response.raise_for_status()

        auth_response = AuthResponse(**response.json())
        self._token = auth_response.access_token
        self._token_expiration = (
            current_time + auth_response.expires_in - 50
        )  # 50s buffer
        return self._token

    async def _get(self, path: str, model: Type[BaseModel]):
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = await self._client.get(f"{self._base_url}{path}", headers=headers)
        # TODO: These lines are bit brittle, and suffer from the same issue as above.
        response.raise_for_status()
        return model(**response.json())

    async def tenants(self):
        return await self._get("/v1/tenants", model=TenantsResponse)

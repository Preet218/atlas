"""Shared HTTP client utilities."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


DEFAULT_TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=30.0,
    write=30.0,
    pool=10.0,
)


class AtlasHttpClient:
    """Thin wrapper around httpx.AsyncClient."""

    def __init__(
        self,
        *,
        timeout: httpx.Timeout | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            timeout=timeout or DEFAULT_TIMEOUT,
            headers=headers,
            follow_redirects=True,
        )

    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        """Perform an HTTP GET request."""

        response = await self._client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response

    async def post(
        self,
        url: str,
        *,
        json: Any | None = None,
    ) -> httpx.Response:
        """Perform an HTTP POST request."""

        response = await self._client.post(
            url,
            json=json,
        )

        response.raise_for_status()

        return response

    async def close(self) -> None:
        """Close the underlying HTTP client."""

        await self._client.aclose()

    async def __aenter__(self) -> "AtlasHttpClient":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        await self.close()

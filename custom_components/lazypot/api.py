"""Thin async HTTP client for the LazyPot smart-home API.

Talks only to a dedicated, access-limited LazyPot smart-home API
endpoint using a scoped integration token -- never the main LazyPot
account login flow.

Response shape: the API returns a plain JSON array/object directly. The
unwrap in async_get_devices stays defensive/tolerant of a legacy-style
wrapped response too, in case a future API version ever wraps results.
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import DEFAULT_API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class LazyPotApiError(Exception):
    """Generic LazyPot API error."""


class LazyPotAuthError(LazyPotApiError):
    """Raised on 401 -- token invalid/expired/revoked. Triggers HA reauth."""


class LazyPotApiClient:
    """Minimal client: validate token, fetch devices + latest measurements."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_token: str,
        base_url: str = DEFAULT_API_BASE_URL,
    ) -> None:
        self._session = session
        self._token = api_token
        self._base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    async def async_validate_token(self) -> None:
        """Raise LazyPotAuthError if the token is not accepted. Used by the
        config flow to validate input before creating the config entry."""
        await self.async_get_devices()

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Fetch the account's LazyPot devices with their latest measurement.

        Response shape per device:

            {
              "connectionId": int,
              "name": str,
              "moistureLevel": float | None,
              "batteryLevel": float | None,
              "waterLevel": float | None,
              "lastWateredOn": str (ISO 8601) | None,
              "lastSeenOn": str (ISO 8601) | None,
              "isOnline": bool,
            }
        """
        body = await self._get_json(f"{self._base_url}/devices")

        # Defensive unwrap: the API returns a plain array directly, but
        # stay tolerant of a legacy-style wrapped response too.
        devices = body.get("response", body) if isinstance(body, dict) else body
        if not isinstance(devices, list):
            _LOGGER.warning("Unexpected devices response shape: %r", body)
            return []
        return devices

    async def async_get_device(self, connection_id: int) -> dict[str, Any]:
        """Fetch a single device by id. Same shape as one entry from async_get_devices()."""
        body = await self._get_json(f"{self._base_url}/devices/{connection_id}")
        if not isinstance(body, dict):
            raise LazyPotApiError(f"Unexpected device response shape: {body!r}")
        return body

    async def async_get_device_history(
        self, connection_id: int, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Fetch the device's most recent readings, newest first.

        Response shape per entry:

            {
              "moistureLevel": float | None,
              "batteryLevel": float | None,
              "waterLevel": float | None,
              "recordedOn": str (ISO 8601),
            }

        `limit` is clamped server-side to 200.
        """
        url = f"{self._base_url}/devices/{connection_id}/history"
        body = await self._get_json(url, params={"limit": limit})
        if not isinstance(body, list):
            _LOGGER.warning("Unexpected device history response shape: %r", body)
            return []
        return body

    async def _get_json(
        self, url: str, params: dict[str, Any] | None = None
    ) -> Any:
        try:
            async with self._session.get(
                url, headers=self._headers(), params=params
            ) as resp:
                if resp.status == 401:
                    raise LazyPotAuthError("Token rejected (401)")
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise LazyPotApiError(f"Network error contacting LazyPot API: {err}") from err

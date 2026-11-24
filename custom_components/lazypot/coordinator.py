"""DataUpdateCoordinator: single poll per interval, fans out to all entities."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LazyPotApiClient, LazyPotApiError, LazyPotAuthError
from .const import DEFAULT_SCAN_INTERVAL_MINUTES, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


class LazyPotCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Polls GetLazyPotsByUser once per cycle; keyed by connectionId."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: LazyPotApiClient
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES),
        )
        self._client = client
        self.entry = entry

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            devices = await self._client.async_get_devices()
        except LazyPotAuthError as err:
            # Surfaces as a reauth flow in the HA UI instead of a silent
            # failure -- token expired/revoked, user must re-generate one.
            raise ConfigEntryAuthFailed("LazyPot token rejected") from err
        except LazyPotApiError as err:
            raise UpdateFailed(str(err)) from err

        return {str(d["connectionId"]): d for d in devices if "connectionId" in d}


def cloud_device_info(
    coordinator: LazyPotCoordinator, connection_id: str
) -> DeviceInfo:
    """Device info for a cloud pot.

    Newer API versions also return the pot's own id ("deviceId"), the same id the pot uses
    when it reports locally. Adding it as a second identifier makes Home Assistant put the
    cloud and local entities of one pot on a single device.
    """
    device = coordinator.data.get(connection_id, {})
    identifiers = {(DOMAIN, connection_id)}
    if device.get("deviceId"):
        identifiers.add((DOMAIN, str(device["deviceId"])))
    return DeviceInfo(
        identifiers=identifiers,
        manufacturer=MANUFACTURER,
        name=device.get("name") or f"LazyPot {connection_id}",
    )

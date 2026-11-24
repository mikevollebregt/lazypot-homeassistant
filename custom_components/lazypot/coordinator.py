"""DataUpdateCoordinator: single poll per interval, fans out to all entities."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

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
        # Last poll result as the API returned it; self.data is this plus newer local reports.
        self._cloud: dict[str, dict[str, Any]] = {}

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            devices = await self._client.async_get_devices()
        except LazyPotAuthError as err:
            # Surfaces as a reauth flow in the HA UI instead of a silent
            # failure -- token expired/revoked, user must re-generate one.
            raise ConfigEntryAuthFailed("LazyPot token rejected") from err
        except LazyPotApiError as err:
            raise UpdateFailed(str(err)) from err

        self._cloud = {
            str(d["connectionId"]): d for d in devices if "connectionId" in d
        }
        return self._with_local(self._cloud)

    # Local reports (see local.py) for pots this account also has. Home Assistant keeps one
    # device per config entry, so a pot with both the app and the LazyPot integration switched
    # on stays the cloud entry's device; its local reports are folded in here whenever they
    # are newer than what the cloud knows.

    def connection_for(self, device_id: str) -> str | None:
        """Connection id of the cloud pot with this device id, if this account has it."""
        wanted = device_id.lower()
        for connection_id, device in self._cloud.items():
            if str(device.get("deviceId") or "").lower() == wanted:
                return connection_id
        return None

    @callback
    def async_local_report(self, device_id: str) -> bool:
        """A local report arrived; True when this account has the pot (and took it)."""
        if self.connection_for(device_id) is None:
            return False
        self.data = self._with_local(self._cloud)
        self.async_update_listeners()
        return True

    def _local_reports(self) -> dict[str, dict[str, Any]]:
        reports: dict[str, dict[str, Any]] = {}
        for obj in self.hass.data.get(DOMAIN, {}).values():
            pots = getattr(obj, "pots", None)
            if isinstance(pots, dict):
                reports.update({k.lower(): v for k, v in pots.items()})
        return reports

    def _with_local(
        self, cloud: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        local = self._local_reports()
        if not local:
            return cloud
        merged: dict[str, dict[str, Any]] = {}
        for connection_id, device in cloud.items():
            report = local.get(str(device.get("deviceId") or "").lower())
            merged[connection_id] = _overlay(device, report) if report else device
        return merged


def _overlay(device: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    """Cloud values, replaced by the local report's when that report is newer."""
    local_seen = dt_util.parse_datetime(str(report.get("last_seen") or ""))
    cloud_seen = dt_util.parse_datetime(str(device.get("lastSeenOn") or ""))
    if local_seen is None or (cloud_seen is not None and cloud_seen >= local_seen):
        return device
    merged = dict(device)
    for cloud_key, local_key in (
        ("moistureLevel", "moisture"),
        ("waterLevel", "water_level"),
        ("batteryLevel", "battery"),
        ("lastWateredOn", "last_watered"),
    ):
        if report.get(local_key) is not None:
            merged[cloud_key] = report[local_key]
    merged["lastSeenOn"] = local_seen.isoformat()
    merged["isOnline"] = True
    merged["source"] = "local"
    return merged


def cloud_device_info(
    coordinator: LazyPotCoordinator, connection_id: str
) -> DeviceInfo:
    """Device info for a cloud pot.

    Keyed on the connection id only. A pot that also reports locally stays this device (see
    LazyPotCoordinator.async_local_report), because Home Assistant does not share a device
    between config entries.
    """
    device = coordinator.data.get(connection_id, {})
    return DeviceInfo(
        identifiers={(DOMAIN, connection_id)},
        manufacturer=MANUFACTURER,
        name=device.get("name") or f"LazyPot {connection_id}",
    )

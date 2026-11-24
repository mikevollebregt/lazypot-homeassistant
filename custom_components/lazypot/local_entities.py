"""Entities for pots reporting to the local entry (see local.py).

Shared base: device info from the pot's own report, availability from the time of the last
report, and live updates through the dispatcher signal the webhook sends.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, LOCAL_STALE_HOURS, MANUFACTURER, SIGNAL_LOCAL_UPDATE
from .local import LocalHub


class LocalPotEntity(Entity):
    """One value of one locally reporting pot."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hub: LocalHub, device_id: str, key: str) -> None:
        self._hub = hub
        self._device_id = device_id
        self._key = key
        self._attr_unique_id = f"local_{device_id}_{key}"
        report = self._report
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer=MANUFACTURER,
            model=report.get("model") or "LazyPot",
            name=report.get("name") or f"LazyPot {device_id[:4]}",
            sw_version=report.get("firmware") or None,
        )

    @property
    def _report(self) -> dict[str, Any]:
        return self._hub.pots.get(self._device_id, {})

    def _value(self, key: str | None = None) -> Any:
        return self._report.get(key or self._key)

    @property
    def available(self) -> bool:
        last_seen = dt_util.parse_datetime(self._report.get("last_seen") or "")
        if last_seen is None:
            return False
        return dt_util.utcnow() - last_seen < timedelta(hours=LOCAL_STALE_HOURS)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_LOCAL_UPDATE.format(self._hub.entry.entry_id, self._device_id),
                self.async_write_ha_state,
            )
        )

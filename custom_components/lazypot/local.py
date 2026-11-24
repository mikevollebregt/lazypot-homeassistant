"""Local mode: LazyPots on the home network push their readings to Home Assistant.

A pot sleeps almost all the time, so Home Assistant can never ask it for data. Instead the pot
(firmware with the "haIntegration" channel switched on) finds Home Assistant via mDNS after
each wake and POSTs one JSON report to a fixed, local-only webhook. One "LazyPot (local)"
config entry receives the reports of every pot in the house and adds each new pot as a device
the first time it reports.

The pot also announces itself as ``_lazypot._tcp`` while it is awake, which is how Home
Assistant offers "New LazyPot found" before the local entry exists.

Last reports are stored on disk so devices keep their last values over a Home Assistant
restart (a pot may not report again for hours).
"""

from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import Any

from aiohttp import web
from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    LOCAL_WEBHOOK_ID,
    SIGNAL_LOCAL_NEW_POT,
    SIGNAL_LOCAL_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
SAVE_DELAY_SECONDS = 10

# Device ids are the pot's own UUID; refuse anything else so a stray POST cannot create junk
# devices with arbitrary names.
_DEVICE_ID_RE = re.compile(r"^[0-9A-Za-z-]{8,64}$")

# Fields a report may carry (see firmware HomeAssistantMqtt.cpp fillState()). Anything else
# is dropped.
_STATE_FIELDS = (
    "moisture",
    "water_level",
    "water_low",
    "battery",
    "battery_voltage",
    "rssi",
    "care_state",
    "mode",
    "last_watered",
    "last_dose_ml",
    "next_check_in",
)


class LocalHub:
    """Keeps the latest report per pot and tells entities when something changed."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.pots: dict[str, dict[str, Any]] = {}
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.local_{entry.entry_id}"
        )

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if data and isinstance(data.get("pots"), dict):
            self.pots = data["pots"]

    @callback
    def _data_to_save(self) -> dict[str, Any]:
        return {"pots": self.pots}

    @callback
    def async_register_webhook(self) -> None:
        webhook.async_register(
            self.hass,
            DOMAIN,
            "LazyPot local reports",
            LOCAL_WEBHOOK_ID,
            self._async_handle_report,
            local_only=True,
            allowed_methods=["POST"],
        )

    @callback
    def async_start_staleness_check(self) -> None:
        """Re-evaluate availability now and then: a silent pot sends no update to trigger it."""

        @callback
        def _refresh(_now: Any) -> None:
            for device_id in self.pots:
                async_dispatcher_send(
                    self.hass,
                    SIGNAL_LOCAL_UPDATE.format(self.entry.entry_id, device_id),
                )

        self.entry.async_on_unload(
            async_track_time_interval(self.hass, _refresh, timedelta(minutes=30))
        )

    @callback
    def async_unregister_webhook(self) -> None:
        webhook.async_unregister(self.hass, LOCAL_WEBHOOK_ID)

    async def _async_handle_report(
        self, hass: HomeAssistant, webhook_id: str, request: web.Request
    ) -> web.Response:
        try:
            payload = await request.json()
        except ValueError:
            return web.json_response({"ok": False, "error": "invalid_json"}, status=400)
        if not isinstance(payload, dict):
            return web.json_response({"ok": False, "error": "invalid_json"}, status=400)

        device_id = payload.get("device_id")
        if not isinstance(device_id, str) or not _DEVICE_ID_RE.match(device_id):
            return web.json_response(
                {"ok": False, "error": "invalid_device_id"}, status=400
            )

        report: dict[str, Any] = {key: payload.get(key) for key in _STATE_FIELDS}
        report["name"] = str(payload.get("name") or f"LazyPot {device_id[:4]}")[:64]
        report["firmware"] = str(payload.get("firmware") or "")[:32]
        report["model"] = str(payload.get("model") or "LazyPot")[:64]
        channels = payload.get("channels")
        report["channels"] = channels if isinstance(channels, dict) else {}
        report["last_seen"] = dt_util.utcnow().isoformat()

        is_new = device_id not in self.pots
        self.pots[device_id] = report
        self._store.async_delay_save(self._data_to_save, SAVE_DELAY_SECONDS)

        if is_new:
            _LOGGER.info("New local LazyPot %s (%s)", report["name"], device_id)
            async_dispatcher_send(
                hass, SIGNAL_LOCAL_NEW_POT.format(self.entry.entry_id), device_id
            )
        else:
            _LOGGER.debug("Report from local LazyPot %s", device_id)
        async_dispatcher_send(
            hass, SIGNAL_LOCAL_UPDATE.format(self.entry.entry_id, device_id)
        )

        # The reply is the place for future settings (switch channels from Home Assistant).
        return web.json_response({"ok": True})

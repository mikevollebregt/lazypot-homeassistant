"""Channel switches for locally reporting pots: LazyPot app, LazyPot integration, MQTT.

A pot sleeps, so a change cannot be applied right away. The switch shows the wanted value
straight away (attribute ``pending: true``) and the pot applies it at its next check-in,
from the reply to its report. The pot has the last word: it refuses to switch on the app
when it was never linked to an account, MQTT when no broker was set up, and any change that
would leave no channel at all. Then the switch falls back to what the pot reports.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_MODE,
    DOMAIN,
    MODE_LOCAL,
    SIGNAL_LOCAL_CLAIMED,
    SIGNAL_LOCAL_NEW_POT,
)
from .coordinator import LazyPotCoordinator, cloud_device_info
from .local import LocalHub
from .local_entities import LocalPotEntity

CHANNELS: tuple[tuple[str, str, str], ...] = (
    ("cloud", "channel_app", "mdi:cellphone"),
    ("integration", "channel_integration", "mdi:home-assistant"),
    ("mqtt", "channel_mqtt", "mdi:access-point-network"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    if entry.data.get(CONF_MODE) != MODE_LOCAL:
        _setup_cloud_switches(hass, entry, async_add_entities)
        return

    hub: LocalHub = hass.data[DOMAIN][entry.entry_id]

    def _entities_for(device_id: str) -> list[LocalChannelSwitch]:
        return [LocalChannelSwitch(hub, device_id, *channel) for channel in CHANNELS]

    @callback
    def _async_new_pot(device_id: str) -> None:
        async_add_entities(_entities_for(device_id))

    async_add_entities(
        [
            e
            for device_id in hub.pots
            if not hub.is_claimed(device_id)
            for e in _entities_for(device_id)
        ]
    )
    entry.async_on_unload(
        async_dispatcher_connect(
            hass, SIGNAL_LOCAL_NEW_POT.format(entry.entry_id), _async_new_pot
        )
    )


class LocalChannelSwitch(LocalPotEntity, SwitchEntity):
    """Switches one channel of a pot at its next check-in."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        hub: LocalHub,
        device_id: str,
        channel: str,
        translation_key: str,
        icon: str,
    ) -> None:
        super().__init__(hub, device_id, f"channel_{channel}")
        self._channel = channel
        self._attr_translation_key = translation_key
        self._attr_icon = icon

    @property
    def _pending(self) -> bool | None:
        return self._hub.wanted.get(self._device_id, {}).get(self._channel)

    @property
    def is_on(self) -> bool | None:
        if self._pending is not None:
            return self._pending
        return self._report.get("channels", {}).get(self._channel)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"pending": self._pending is not None}

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._hub.async_set_channel(self._device_id, self._channel, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._hub.async_set_channel(self._device_id, self._channel, False)


def _find_hub(hass: HomeAssistant, device_id: str) -> LocalHub | None:
    """The local entry that receives this pot's reports, if any."""
    for obj in hass.data.get(DOMAIN, {}).values():
        if isinstance(obj, LocalHub) and device_id in obj.pots:
            return obj
    return None


def _setup_cloud_switches(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Channel switches on account pots that also report locally.

    They are added the first time such a pot's local report arrives (or at startup when one
    was stored), on the cloud device, because the pot is that entry's device.
    """
    coordinator: LazyPotCoordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    @callback
    def _async_add_for(device_id: str) -> None:
        connection_id = coordinator.connection_for(device_id)
        if connection_id is None or connection_id in added:
            return
        added.add(connection_id)
        async_add_entities(
            CloudChannelSwitch(coordinator, connection_id, device_id, *channel)
            for channel in CHANNELS
        )

    for obj in hass.data.get(DOMAIN, {}).values():
        if isinstance(obj, LocalHub):
            for device_id in list(obj.pots):
                _async_add_for(device_id)
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_LOCAL_CLAIMED, _async_add_for)
    )


class CloudChannelSwitch(CoordinatorEntity[LazyPotCoordinator], SwitchEntity):
    """The same channel switch, on an account pot that also reports locally."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LazyPotCoordinator,
        connection_id: str,
        device_id: str,
        channel: str,
        translation_key: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._channel = channel
        self._attr_translation_key = translation_key
        self._attr_icon = icon
        self._attr_unique_id = f"{connection_id}_channel_{channel}"
        self._attr_device_info = cloud_device_info(coordinator, connection_id)

    @property
    def _hub(self) -> LocalHub | None:
        return _find_hub(self.hass, self._device_id)

    @property
    def available(self) -> bool:
        return self._hub is not None

    @property
    def _pending(self) -> bool | None:
        hub = self._hub
        return hub.wanted.get(self._device_id, {}).get(self._channel) if hub else None

    @property
    def is_on(self) -> bool | None:
        if self._pending is not None:
            return self._pending
        hub = self._hub
        if hub is None:
            return None
        return hub.pots[self._device_id].get("channels", {}).get(self._channel)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"pending": self._pending is not None}

    async def async_turn_on(self, **kwargs: Any) -> None:
        if hub := self._hub:
            hub.async_set_channel(self._device_id, self._channel, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        if hub := self._hub:
            hub.async_set_channel(self._device_id, self._channel, False)

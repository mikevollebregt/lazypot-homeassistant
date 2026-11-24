"""Derived binary sensors: low battery / low water flags for easy automations."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_MODE,
    DOMAIN,
    LOW_BATTERY_THRESHOLD,
    LOW_WATER_THRESHOLD,
    MANUFACTURER,
    MODE_LOCAL,
    SIGNAL_LOCAL_NEW_POT,
)
from .coordinator import LazyPotCoordinator
from .local import LocalHub
from .local_entities import LocalPotEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    if entry.data.get(CONF_MODE) == MODE_LOCAL:
        hub: LocalHub = hass.data[DOMAIN][entry.entry_id]

        def _entities_for(device_id: str) -> list[BinarySensorEntity]:
            return [LocalWaterLowBinarySensor(hub, device_id)]

        @callback
        def _async_new_pot(device_id: str) -> None:
            async_add_entities(_entities_for(device_id))

        async_add_entities(
            [e for device_id in hub.pots for e in _entities_for(device_id)]
        )
        entry.async_on_unload(
            async_dispatcher_connect(
                hass, SIGNAL_LOCAL_NEW_POT.format(entry.entry_id), _async_new_pot
            )
        )
        return

    coordinator: LazyPotCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []
    for connection_id in coordinator.data:
        entities.append(LazyPotOnlineBinarySensor(coordinator, connection_id))
        entities.append(
            LazyPotThresholdBinarySensor(
                coordinator,
                connection_id,
                key="low_battery",
                name="Low battery",
                value_key="batteryLevel",
                threshold=LOW_BATTERY_THRESHOLD,
                device_class=BinarySensorDeviceClass.BATTERY,
            )
        )
        entities.append(
            LazyPotThresholdBinarySensor(
                coordinator,
                connection_id,
                key="low_water",
                name="Low water",
                value_key="waterLevel",
                threshold=LOW_WATER_THRESHOLD,
                device_class=BinarySensorDeviceClass.PROBLEM,
            )
        )
    async_add_entities(entities)


class LazyPotOnlineBinarySensor(
    CoordinatorEntity[LazyPotCoordinator], BinarySensorEntity
):
    """Reflects the API's own isOnline flag (reported within the last 24h)."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: LazyPotCoordinator, connection_id: str) -> None:
        super().__init__(coordinator)
        self._connection_id = connection_id
        self._attr_name = "Online"
        self._attr_unique_id = f"{connection_id}_online"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, connection_id)},
            manufacturer=MANUFACTURER,
            name=coordinator.data.get(connection_id, {}).get("name")
            or f"LazyPot {connection_id}",
        )

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.data.get(self._connection_id, {})
        return bool(device.get("isOnline"))


class LazyPotThresholdBinarySensor(
    CoordinatorEntity[LazyPotCoordinator], BinarySensorEntity
):
    def __init__(
        self,
        coordinator: LazyPotCoordinator,
        connection_id: str,
        *,
        key: str,
        name: str,
        value_key: str,
        threshold: float,
        device_class: BinarySensorDeviceClass,
    ) -> None:
        super().__init__(coordinator)
        self._connection_id = connection_id
        self._value_key = value_key
        self._threshold = threshold
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_unique_id = f"{connection_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, connection_id)},
            manufacturer=MANUFACTURER,
            name=coordinator.data.get(connection_id, {}).get("name")
            or f"LazyPot {connection_id}",
        )

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.data.get(self._connection_id, {})
        value = device.get(self._value_key)
        if value is None:
            return None
        return value < self._threshold


class LocalWaterLowBinarySensor(LocalPotEntity, BinarySensorEntity):
    """On when the pot reports its water tank as (nearly) empty."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "water_tank_empty"

    def __init__(self, hub: LocalHub, device_id: str) -> None:
        super().__init__(hub, device_id, "water_low")

    @property
    def is_on(self) -> bool | None:
        value = self._value()
        if value is None:
            return None
        return value == "ON"

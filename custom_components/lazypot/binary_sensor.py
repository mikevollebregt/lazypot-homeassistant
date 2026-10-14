"""Derived binary sensors: low battery / low water flags for easy automations."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOW_BATTERY_THRESHOLD, LOW_WATER_THRESHOLD, MANUFACTURER
from .coordinator import LazyPotCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
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


class LazyPotOnlineBinarySensor(CoordinatorEntity[LazyPotCoordinator], BinarySensorEntity):
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
            name=coordinator.data.get(connection_id, {}).get("name") or f"LazyPot {connection_id}",
        )

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.data.get(self._connection_id, {})
        return bool(device.get("isOnline"))


class LazyPotThresholdBinarySensor(CoordinatorEntity[LazyPotCoordinator], BinarySensorEntity):
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
            name=coordinator.data.get(connection_id, {}).get("name") or f"LazyPot {connection_id}",
        )

    @property
    def is_on(self) -> bool | None:
        device = self.coordinator.data.get(self._connection_id, {})
        value = device.get(self._value_key)
        if value is None:
            return None
        return value < self._threshold

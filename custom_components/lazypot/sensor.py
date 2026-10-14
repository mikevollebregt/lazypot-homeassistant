"""LazyPot sensor entities: moisture, battery, water level, last watered."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MANUFACTURER
from .coordinator import LazyPotCoordinator


@dataclass(frozen=True, kw_only=True)
class LazyPotSensorDescription(SensorEntityDescription):
    value_key: str = ""


SENSOR_TYPES: tuple[LazyPotSensorDescription, ...] = (
    LazyPotSensorDescription(
        key="moisture",
        value_key="moistureLevel",
        name="Moisture",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
    ),
    LazyPotSensorDescription(
        key="battery",
        value_key="batteryLevel",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    LazyPotSensorDescription(
        key="water_level",
        value_key="waterLevel",
        name="Water level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cup-water",
    ),
    LazyPotSensorDescription(
        key="last_watered",
        value_key="lastWateredOn",
        name="Last watered",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    LazyPotSensorDescription(
        key="last_seen",
        value_key="lastSeenOn",
        name="Last seen",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LazyPotCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        LazyPotSensor(coordinator, connection_id, description)
        for connection_id in coordinator.data
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class LazyPotSensor(CoordinatorEntity[LazyPotCoordinator], SensorEntity):
    entity_description: LazyPotSensorDescription

    def __init__(
        self,
        coordinator: LazyPotCoordinator,
        connection_id: str,
        description: LazyPotSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._connection_id = connection_id
        self._attr_unique_id = f"{connection_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, connection_id)},
            manufacturer=MANUFACTURER,
            name=self._device_name,
        )

    @property
    def _device_name(self) -> str:
        device = self.coordinator.data.get(self._connection_id, {})
        return device.get("name") or f"LazyPot {self._connection_id}"

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._connection_id, {})
        value = device.get(self.entity_description.value_key)
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP and value:
            return dt_util.parse_datetime(value)
        return value

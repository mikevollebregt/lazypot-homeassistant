"""LazyPot sensor entities: moisture, battery, water level, last watered."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CONF_MODE, DOMAIN, MODE_LOCAL, SIGNAL_LOCAL_NEW_POT
from .coordinator import LazyPotCoordinator, cloud_device_info
from .local import LocalHub
from .local_entities import LocalPotEntity


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


LOCAL_SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="moisture",
        translation_key="soil_moisture",
        device_class=SensorDeviceClass.MOISTURE,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="water_level",
        translation_key="water_tank",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cup-water",
    ),
    SensorEntityDescription(
        key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="last_watered",
        translation_key="last_watered",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:watering-can",
    ),
    SensorEntityDescription(
        key="last_dose_ml",
        translation_key="last_dose",
        device_class=SensorDeviceClass.VOLUME,
        native_unit_of_measurement=UnitOfVolume.MILLILITERS,
        suggested_display_precision=0,
        icon="mdi:water",
    ),
    SensorEntityDescription(
        key="care_state",
        translation_key="care_state",
        icon="mdi:sprout",
    ),
    SensorEntityDescription(
        key="next_check_in",
        translation_key="next_check_in",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:timer-sand",
    ),
    SensorEntityDescription(
        key="last_seen",
        translation_key="last_seen",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="rssi",
        translation_key="wifi_signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    if entry.data.get(CONF_MODE) == MODE_LOCAL:
        hub: LocalHub = hass.data[DOMAIN][entry.entry_id]

        def _entities_for(device_id: str) -> list[LocalPotSensor]:
            return [LocalPotSensor(hub, device_id, d) for d in LOCAL_SENSOR_TYPES]

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
        self._attr_device_info = cloud_device_info(coordinator, connection_id)

    @property
    def _device_name(self) -> str:
        device = self.coordinator.data.get(self._connection_id, {})
        return device.get("name") or f"LazyPot {self._connection_id}"

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._connection_id, {})
        value = device.get(self.entity_description.value_key)
        if (
            self.entity_description.device_class == SensorDeviceClass.TIMESTAMP
            and value
        ):
            return dt_util.parse_datetime(value)
        return value


class LocalPotSensor(LocalPotEntity, SensorEntity):
    """A reading from a pot that reports to Home Assistant over the local network."""

    def __init__(
        self, hub: LocalHub, device_id: str, description: SensorEntityDescription
    ) -> None:
        super().__init__(hub, device_id, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        value = self._value()
        if value is None:
            return None
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            return dt_util.parse_datetime(str(value))
        return value

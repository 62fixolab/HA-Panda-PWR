# Copyright (c) 2026 FixoLab
"""Sensor platform for PandaPWR integration in Home Assistant."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COUNTDOWN_STATES
from .coordinator import PandaPWRConfigEntry, PandaPWRCoordinator, PandaPWREntity


@dataclass(frozen=True, kw_only=True)
class PandaPWRSensorDescription(SensorEntityDescription):
    """Sensor bound to one field of the device reply."""

    data_key: str
    value_fn: Callable[[Any], Any] = lambda value: value


SENSORS = (
    PandaPWRSensorDescription(
        key="countdown_state",
        data_key="countdown_state",
        device_class=SensorDeviceClass.ENUM,
        options=list(COUNTDOWN_STATES.values()),
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=COUNTDOWN_STATES.get,
    ),
    PandaPWRSensorDescription(
        key="auto_poweroff",
        data_key="auto_poweroff",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PandaPWRSensorDescription(
        key="countdown",
        data_key="countdown",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    PandaPWRSensorDescription(
        key="voltage",
        data_key="voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PandaPWRSensorDescription(
        key="current",
        data_key="current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PandaPWRSensorDescription(
        key="power",
        data_key="power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PandaPWRSensorDescription(
        key="energy_usage",
        data_key="ele",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PandaPWRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform for PandaPWR."""
    async_add_entities(
        PandaPWRSensor(entry.runtime_data, description) for description in SENSORS
    )


class PandaPWRSensor(PandaPWREntity, SensorEntity):
    """Sensor reporting one field of the last poll."""

    entity_description: PandaPWRSensorDescription

    def __init__(
        self, coordinator: PandaPWRCoordinator, description: PandaPWRSensorDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the value reported by the device in the last poll."""
        value = self.coordinator.data.get(self.entity_description.data_key)
        return None if value is None else self.entity_description.value_fn(value)

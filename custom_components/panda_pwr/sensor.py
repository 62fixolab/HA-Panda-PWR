# Copyright (c) 2026 FixoLab
"""Sensor platform for PandaPWR integration in Home Assistant."""

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.components.sensor.const import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PandaPWRCoordinator, PandaPWREntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform for PandaPWR."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            CountdownStateSensor(coordinator),
            AutoPoweroffSensor(coordinator),
            CountdownSensor(coordinator),
            VoltageSensor(coordinator),
            CurrentSensor(coordinator),
            PowerSensor(coordinator),
            EnergyUsageSensor(coordinator),
        ]
    )


class PandaPWRSensor(PandaPWREntity, SensorEntity):
    """Base class for PandaPWR sensors."""

    def __init__(self, coordinator: PandaPWRCoordinator, sensor_info: dict) -> None:
        """Initialize the sensor with common attributes."""
        super().__init__(coordinator)
        self._data_key = sensor_info["data_key"]
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{self._device_id}_{sensor_info['unique_id_suffix']}"
        self._attr_native_unit_of_measurement = sensor_info.get(
            "native_unit_of_measurement"
        )
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_state_class = sensor_info.get("state_class")

    @property
    def native_value(self) -> Any:
        """Return the value reported by the device in the last poll."""
        return self.coordinator.data.get(self._data_key)


class CountdownStateSensor(PandaPWRSensor):
    """Sensor for monitoring countdown state on a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Countdown State",
            "unique_id_suffix": "countdown_state",
            "data_key": "countdown_state",
        }
        super().__init__(coordinator, sensor_info)


class AutoPoweroffSensor(PandaPWRSensor):
    """Sensor for monitoring auto power-off state on a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Auto Poweroff",
            "unique_id_suffix": "auto_poweroff",
            "data_key": "auto_poweroff",
        }
        super().__init__(coordinator, sensor_info)


class CountdownSensor(PandaPWRSensor):
    """Sensor for monitoring countdown timer on a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Countdown",
            "unique_id_suffix": "countdown",
            "data_key": "countdown",
            "native_unit_of_measurement": "s",
        }
        super().__init__(coordinator, sensor_info)


class VoltageSensor(PandaPWRSensor):
    """Sensor for monitoring voltage on a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Voltage",
            "unique_id_suffix": "voltage",
            "data_key": "voltage",
            "native_unit_of_measurement": UnitOfElectricPotential.VOLT,
            "device_class": SensorDeviceClass.VOLTAGE,
            "state_class": SensorStateClass.MEASUREMENT,
        }
        super().__init__(coordinator, sensor_info)


class CurrentSensor(PandaPWRSensor):
    """Sensor for monitoring current on a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Current",
            "unique_id_suffix": "current",
            "data_key": "current",
            "native_unit_of_measurement": UnitOfElectricCurrent.AMPERE,
            "device_class": SensorDeviceClass.CURRENT,
            "state_class": SensorStateClass.MEASUREMENT,
        }
        super().__init__(coordinator, sensor_info)


class PowerSensor(PandaPWRSensor):
    """Sensor for monitoring power on a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Power",
            "unique_id_suffix": "power",
            "data_key": "power",
            "native_unit_of_measurement": UnitOfPower.WATT,
            "device_class": SensorDeviceClass.POWER,
            "state_class": SensorStateClass.MEASUREMENT,
        }
        super().__init__(coordinator, sensor_info)


class EnergyUsageSensor(PandaPWRSensor):
    """Sensor for monitoring energy usage on a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Energy Usage",
            "unique_id_suffix": "energy_usage",
            "data_key": "ele",
            "native_unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": SensorDeviceClass.ENERGY,
            "state_class": SensorStateClass.TOTAL_INCREASING,
        }
        super().__init__(coordinator, sensor_info)

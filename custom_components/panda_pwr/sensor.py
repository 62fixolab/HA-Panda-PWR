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


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform for PandaPWR."""
    api = hass.data[DOMAIN][entry.entry_id]
    device_id = f"pandapwr_{entry.data['ip_address']}"
    async_add_entities(
        [
            CountdownStateSensor(api, entry, device_id),
            AutoPoweroffSensor(api, entry, device_id),
            CountdownSensor(api, entry, device_id),
            VoltageSensor(api, entry, device_id),
            CurrentSensor(api, entry, device_id),
            PowerSensor(api, entry, device_id),
            EnergyUsageSensor(api, entry, device_id),
        ],
        update_before_add=True,
    )


class PandaPWRSensor(SensorEntity):
    """Base class for PandaPWR sensors."""

    def __init__(
        self,
        api: Any,
        entry: ConfigEntry,
        device_id: str,
        sensor_info: dict,
    ) -> None:
        """Initialize the sensor with common attributes."""
        self._api = api
        self._entry = entry
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{device_id}_{sensor_info['unique_id_suffix']}"
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = sensor_info.get(
            "native_unit_of_measurement"
        )
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_state_class = sensor_info.get("state_class")
        self._device_id = device_id

    async def async_update(self) -> None:
        """Fetch latest state data from the device."""
        data = await self._api.get_data()
        self.process_data(data)

    @property
    def device_info(self) -> dict:
        """Return device information to group in the UI."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": "Panda PWR",
            "manufacturer": "Panda",
            "model": "PWR Device",
            "sw_version": "1.0",
        }

    def process_data(self, data: dict) -> None:
        """Process data received from the API."""
        raise NotImplementedError


class CountdownStateSensor(PandaPWRSensor):
    """Sensor for monitoring countdown state on a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Countdown State",
            "unique_id_suffix": "countdown_state",
        }
        super().__init__(api, entry, device_id, sensor_info)

    def process_data(self, data: dict) -> None:
        """Process countdown state data from the API."""
        self._attr_native_value = data.get("countdown_state")


class AutoPoweroffSensor(PandaPWRSensor):
    """Sensor for monitoring auto power-off state on a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Auto Poweroff",
            "unique_id_suffix": "auto_poweroff",
        }
        super().__init__(api, entry, device_id, sensor_info)

    def process_data(self, data: dict) -> None:
        """Process auto power-off data from the API."""
        self._attr_native_value = data.get("auto_poweroff")


class CountdownSensor(PandaPWRSensor):
    """Sensor for monitoring countdown timer on a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Countdown",
            "unique_id_suffix": "countdown",
            "native_unit_of_measurement": "s",
        }
        super().__init__(api, entry, device_id, sensor_info)

    def process_data(self, data: dict) -> None:
        """Process countdown timer data from the API."""
        self._attr_native_value = data.get("countdown")


class VoltageSensor(PandaPWRSensor):
    """Sensor for monitoring voltage on a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Voltage",
            "unique_id_suffix": "voltage",
            "native_unit_of_measurement": UnitOfElectricPotential.VOLT,
            "device_class": SensorDeviceClass.VOLTAGE,
            "state_class": SensorStateClass.MEASUREMENT,
        }
        super().__init__(api, entry, device_id, sensor_info)

    def process_data(self, data: dict) -> None:
        """Process voltage data from the API."""
        self._attr_native_value = data.get("voltage") or 0.0


class CurrentSensor(PandaPWRSensor):
    """Sensor for monitoring current on a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Current",
            "unique_id_suffix": "current",
            "native_unit_of_measurement": UnitOfElectricCurrent.AMPERE,
            "device_class": SensorDeviceClass.CURRENT,
            "state_class": SensorStateClass.MEASUREMENT,
        }
        super().__init__(api, entry, device_id, sensor_info)

    def process_data(self, data: dict) -> None:
        """Process current data from the API."""
        self._attr_native_value = data.get("current") or 0.0


class PowerSensor(PandaPWRSensor):
    """Sensor for monitoring power on a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Power",
            "unique_id_suffix": "power",
            "native_unit_of_measurement": UnitOfPower.WATT,
            "device_class": SensorDeviceClass.POWER,
            "state_class": SensorStateClass.MEASUREMENT,
        }
        super().__init__(api, entry, device_id, sensor_info)

    def process_data(self, data: dict) -> None:
        """Process power data from the API."""
        self._attr_native_value = data.get("power") or 0.0


class EnergyUsageSensor(PandaPWRSensor):
    """Sensor for monitoring energy usage on a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the sensor."""
        sensor_info = {
            "name": "Energy Usage",
            "unique_id_suffix": "energy_usage",
            "native_unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": SensorDeviceClass.ENERGY,
            "state_class": SensorStateClass.TOTAL_INCREASING,
        }
        super().__init__(api, entry, device_id, sensor_info)

    def process_data(self, data: dict) -> None:
        """Process energy usage data from the API."""
        self._attr_native_value = data.get("ele") or 0.0

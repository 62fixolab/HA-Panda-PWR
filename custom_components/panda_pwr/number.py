# Copyright (c) 2026 FixoLab
"""Number platform for PandaPWR integration in Home Assistant."""

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_COUNTDOWN_SECONDS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the number sensor platform from a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]
    device_id = f"pandapwr_{entry.data['ip_address']}"
    async_add_entities(
        [PandaPWRCountdownTimer(api, entry, device_id)],
        update_before_add=True,
    )


class PandaPWRNumber(NumberEntity):
    """Base class for PandaPWR numbers."""

    def __init__(
        self,
        api: Any,
        entry: ConfigEntry,
        device_id: str,
        number_info: dict,
    ) -> None:
        """Initialize the sensor with common attributes."""
        self._api = api
        self._entry = entry
        self._attr_name = number_info.get("name")
        self._attr_unique_id = f"{device_id}_{number_info['unique_id_suffix']}"
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = number_info.get(
            "native_unit_of_measurement"
        )
        self._attr_device_class = number_info.get("device_class")
        self._attr_state_class = number_info.get("state_class")
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


class PandaPWRCountdownTimer(PandaPWRNumber):
    """PandaPWRCountdownTimer."""

    def __init__(self, api: Any, entry: ConfigEntry, device_id: str) -> None:
        """Initialize the number."""
        number_info = {
            "name": "Countdown Time",
            "unique_id_suffix": "countdown_time",
            "native_unit_of_measurement": "s",
            "device_class": "DURATION",
        }
        super().__init__(api, entry, device_id, number_info)
        self._attr_native_max_value = MAX_COUNTDOWN_SECONDS
        self._attr_mode = "box"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._api.set_countdown_timer(int(value))

    def process_data(self, data: dict) -> None:
        """Process data received from the API."""
        self._attr_native_value = data.get("countdown")

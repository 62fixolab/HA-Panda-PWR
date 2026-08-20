# Copyright (c) 2026 FixoLab
"""Switch platform for PandaPWR integration in Home Assistant."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up switch platform for PandaPWR."""
    api = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [PowerSwitch(api, entry, hass), UsbSwitch(api, entry, hass)],
        update_before_add=True,
    )


class PandaPWRSwitch(SwitchEntity):
    """Base class for a PandaPWR switch."""

    def __init__(self, api: Any, entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the switch."""
        self._api = api
        self._entry = entry
        self._hass = hass
        self._attr_is_on = None
        self._device_id = f"pandapwr_{self._entry.data['ip_address']}"

    async def async_update(self) -> None:
        """Fetch latest state data from the device."""
        data = await self._api.get_data()
        self.process_data(data)

    @property
    def device_info(self) -> dict:
        """Return device information for grouping in the UI."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": "Panda PWR",
            "manufacturer": "Panda",
            "model": "PWR Device",
            "sw_version": "1.0",
        }

    def process_data(self, data: dict) -> None:
        """Process API data."""
        raise NotImplementedError


class PowerSwitch(PandaPWRSwitch):
    """Switch entity for controlling the power state of a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the PowerSwitch."""
        super().__init__(api, entry, hass)
        self._attr_name = "Power Switch"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_unique_id = f"{self._device_id}_power_switch"

    async def async_turn_on(self) -> None:
        """Turn on the power switch."""
        await self._api.set_power_state(1)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn off the power switch."""
        await self._api.set_power_state(0)
        self._attr_is_on = False
        self.async_write_ha_state()

    def process_data(self, data: dict) -> None:
        """Process power state data from the API."""
        self._attr_is_on = data.get("power_state") == 1


class UsbSwitch(PandaPWRSwitch):
    """Switch entity for controlling the USB state of a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the UsbSwitch."""
        super().__init__(api, entry, hass)
        self._attr_name = "USB Switch"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_unique_id = f"{self._device_id}_usb_switch"

    async def async_turn_on(self) -> None:
        """Turn on the USB switch."""
        await self._api.set_usb_state(1)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn off the USB switch."""
        await self._api.set_usb_state(0)
        self._attr_is_on = False
        self.async_write_ha_state()

    def process_data(self, data: dict) -> None:
        """Process USB state data from the API."""
        self._attr_is_on = data.get("usb_state") == 1

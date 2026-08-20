# Copyright (c) 2026 FixoLab
"""Binary sensor platform for PandaPWR integration in Home Assistant."""

from typing import Any

import aiohttp
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary sensor platform from a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [PowerStateBinarySensor(api, entry), UsbStateBinarySensor(api, entry)],
        update_before_add=True,
    )


class PandaPWRBinarySensor(BinarySensorEntity):
    """Base class for a PandaPWR binary sensor."""

    def __init__(self, api: Any, entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        self._api = api
        self._entry = entry
        self._attr_is_on = None
        self._attr_available = False
        self._device_id = f"pandapwr_{self._entry.data['ip_address']}"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            data = await self._api.get_data()
            self._attr_available = True
            self.process_data(data)
        except aiohttp.ClientError:
            self._attr_available = False

    async def async_added_to_hass(self) -> None:
        """Subscribe to update signal."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{DOMAIN}_update_signal", self.async_update
            )
        )

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

    def process_data(self, data: Any) -> None:
        """Process data received from the API."""
        raise NotImplementedError


class PowerStateBinarySensor(PandaPWRBinarySensor):
    """Binary sensor for monitoring the power state of a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry) -> None:
        """Initialize the PowerStateBinarySensor."""
        super().__init__(api, entry)
        self._attr_name = "Power State"
        self._attr_device_class = BinarySensorDeviceClass.POWER
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_unique_id = f"{self._device_id}_power_state"

    def process_data(self, data: Any) -> None:
        """Process power state data from the API."""
        self._attr_is_on = data.get("power_state") == 1


class UsbStateBinarySensor(PandaPWRBinarySensor):
    """Binary sensor for monitoring the USB state of a PandaPWR device."""

    def __init__(self, api: Any, entry: ConfigEntry) -> None:
        """Initialize the UsbStateBinarySensor."""
        super().__init__(api, entry)
        self._attr_name = "USB State"
        self._attr_device_class = BinarySensorDeviceClass.POWER
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_unique_id = f"{self._device_id}_usb_state"

    def process_data(self, data: Any) -> None:
        """Process USB state data from the API."""
        self._attr_is_on = data.get("usb_state") == 1

# Copyright (c) 2026 FixoLab
"""Button platform for PandaPWR integration in Home Assistant."""

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up button platform for PandaPWR."""
    api = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [EnergyUsageResetButton(api, entry), FactoryResetButton(api, entry)],
        update_before_add=True,
    )


class PandaPWRButton(ButtonEntity):
    """Base class for PandaPWR buttons."""

    def __init__(self, api: Any, entry: ConfigEntry) -> None:
        """Initialize the button."""
        self._api = api
        self._entry = entry
        self._device_id = f"pandapwr_{self._entry.data['ip_address']}"

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


class EnergyUsageResetButton(PandaPWRButton):
    """Button to reset energy usage statistics."""

    def __init__(self, api: Any, entry: ConfigEntry) -> None:
        """Initialize the energy usage reset button."""
        super().__init__(api, entry)
        self._attr_name = "Reset Energy Usage"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_unique_id = "pandapwr_energy_usage_reset_button"

    async def async_press(self) -> None:
        """Reset the energy usage statistics."""
        await self._api.reset_energy_usage()
        self.async_write_ha_state()


class FactoryResetButton(PandaPWRButton):
    """Button to perform a factory reset."""

    def __init__(self, api: Any, entry: ConfigEntry) -> None:
        """Initialize the factory reset button."""
        super().__init__(api, entry)
        self._attr_name = "Factory Reset"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_unique_id = "pandapwr_factory_reset_button"

    async def async_press(self) -> None:
        """Reset the factory settings."""
        await self._api.reset_factory_settings()
        self.async_write_ha_state()

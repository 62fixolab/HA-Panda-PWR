# Copyright (c) 2026 FixoLab
"""Button platform for PandaPWR integration in Home Assistant."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PandaPWRCoordinator, PandaPWREntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up button platform for PandaPWR."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [EnergyUsageResetButton(coordinator), FactoryResetButton(coordinator)]
    )


class PandaPWRButton(PandaPWREntity, ButtonEntity):
    """Base class for PandaPWR buttons."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_entity_category = EntityCategory.CONFIG


class EnergyUsageResetButton(PandaPWRButton):
    """Button to reset energy usage statistics."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the energy usage reset button."""
        super().__init__(coordinator)
        self._attr_name = "Reset Energy Usage"
        self._attr_unique_id = f"{self._device_id}_energy_usage_reset_button"

    async def async_press(self) -> None:
        """Reset the energy usage statistics."""
        if not await self._api.reset_energy_usage():
            msg = "Panda PWR did not accept the energy usage reset"
            raise HomeAssistantError(msg)
        self.coordinator.async_apply_write({"ele": 0})


class FactoryResetButton(PandaPWRButton):
    """Button to perform a factory reset."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the factory reset button."""
        super().__init__(coordinator)
        self._attr_name = "Factory Reset"
        self._attr_unique_id = f"{self._device_id}_factory_reset_button"

    async def async_press(self) -> None:
        """Reset the factory settings."""
        if not await self._api.do_factory_reset():
            msg = "Panda PWR did not accept the factory reset"
            raise HomeAssistantError(msg)

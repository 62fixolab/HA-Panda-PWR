# Copyright (c) 2026 FixoLab
"""Number platform for PandaPWR integration in Home Assistant."""

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_COUNTDOWN_SECONDS
from .coordinator import PandaPWRCoordinator, PandaPWREntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the number sensor platform from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PandaPWRCountdownTimer(coordinator)])


class PandaPWRCountdownTimer(PandaPWREntity, NumberEntity):
    """Countdown timer of a PandaPWR device, in seconds."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._attr_name = "Countdown Time"
        self._attr_unique_id = f"{self._device_id}_countdown_time"
        self._attr_native_unit_of_measurement = "s"
        self._attr_device_class = NumberDeviceClass.DURATION
        self._attr_native_max_value = MAX_COUNTDOWN_SECONDS
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self) -> float | None:
        """Return the countdown reported by the device in the last poll."""
        return self.coordinator.data.get("countdown")

    async def async_set_native_value(self, value: float) -> None:
        """Send the new countdown to the device."""
        if not await self._api.set_countdown_timer(int(value)):
            msg = "Panda PWR did not accept the countdown change"
            raise HomeAssistantError(msg)
        await self.coordinator.async_request_refresh()

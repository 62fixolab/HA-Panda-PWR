# Copyright (c) 2026 FixoLab
"""Switch platform for PandaPWR integration in Home Assistant."""

from collections.abc import Awaitable, Callable
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up switch platform for PandaPWR."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PowerSwitch(coordinator), UsbSwitch(coordinator)])


class PandaPWRSwitch(PandaPWREntity, SwitchEntity):
    """Base class for a PandaPWR switch."""

    _data_key: str

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def is_on(self) -> bool:
        """Return whether the output is on according to the last poll."""
        return self.coordinator.data.get(self._data_key) == 1

    def _setter(self) -> Callable[[int], Awaitable[bool]]:
        """Return the API call that changes this output."""
        raise NotImplementedError

    async def _async_set(self, state: int) -> None:
        """Send the new state and refresh so every entity reflects it."""
        if not await self._setter()(state):
            msg = f"Panda PWR did not accept the {self.name} change"
            raise HomeAssistantError(msg)
        self.coordinator.data[self._data_key] = state
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the output."""
        await self._async_set(1)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the output."""
        await self._async_set(0)


class PowerSwitch(PandaPWRSwitch):
    """Switch entity for controlling the power state of a PandaPWR device."""

    _data_key = "power_state"

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the PowerSwitch."""
        super().__init__(coordinator)
        self._attr_name = "Power Switch"
        self._attr_unique_id = f"{self._device_id}_power_switch"

    def _setter(self) -> Callable[[int], Awaitable[bool]]:
        return self._api.set_power_state


class UsbSwitch(PandaPWRSwitch):
    """Switch entity for controlling the USB state of a PandaPWR device."""

    _data_key = "usb_state"

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the UsbSwitch."""
        super().__init__(coordinator)
        self._attr_name = "USB Switch"
        self._attr_unique_id = f"{self._device_id}_usb_switch"

    def _setter(self) -> Callable[[int], Awaitable[bool]]:
        return self._api.set_usb_state

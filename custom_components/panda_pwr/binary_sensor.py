# Copyright (c) 2026 FixoLab
"""Binary sensor platform for PandaPWR integration in Home Assistant."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)

from .const import DOMAIN
from .coordinator import PandaPWRCoordinator, PandaPWREntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary sensor platform from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [PowerStateBinarySensor(coordinator), UsbStateBinarySensor(coordinator)]
    )


class PandaPWRBinarySensor(PandaPWREntity, BinarySensorEntity):
    """Base class for a PandaPWR binary sensor."""

    _data_key: str

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_device_class = BinarySensorDeviceClass.POWER
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool:
        """Return whether the output is on according to the last poll."""
        return self.coordinator.data.get(self._data_key) == 1


class PowerStateBinarySensor(PandaPWRBinarySensor):
    """Binary sensor for monitoring the power state of a PandaPWR device."""

    _data_key = "power_state"

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the PowerStateBinarySensor."""
        super().__init__(coordinator)
        self._attr_name = "Power State"
        self._attr_unique_id = f"{self._device_id}_power_state"


class UsbStateBinarySensor(PandaPWRBinarySensor):
    """Binary sensor for monitoring the USB state of a PandaPWR device."""

    _data_key = "usb_state"

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the UsbStateBinarySensor."""
        super().__init__(coordinator)
        self._attr_name = "USB State"
        self._attr_unique_id = f"{self._device_id}_usb_state"

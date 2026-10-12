# Copyright (c) 2026 FixoLab
"""Binary sensor platform for PandaPWR integration in Home Assistant."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import PandaPWRConfigEntry, PandaPWRCoordinator, PandaPWREntity

# translation key / unique ID suffix -> field of the device reply
BINARY_SENSORS = {"power_state": "power_state", "usb_state": "usb_state"}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PandaPWRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform from a config entry."""
    async_add_entities(
        PandaPWRBinarySensor(entry.runtime_data, key, data_key)
        for key, data_key in BINARY_SENSORS.items()
    )


class PandaPWRBinarySensor(PandaPWREntity, BinarySensorEntity):
    """Binary sensor reporting whether an output is on."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: PandaPWRCoordinator, key: str, data_key: str
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, key)
        self._data_key = data_key

    @property
    def is_on(self) -> bool:
        """Return whether the output is on according to the last poll."""
        return self.coordinator.data.get(self._data_key) == 1

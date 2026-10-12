# Copyright (c) 2026 FixoLab
"""Number platform for PandaPWR integration in Home Assistant."""

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import MAX_COUNTDOWN_SECONDS
from .coordinator import PandaPWRConfigEntry, PandaPWREntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PandaPWRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform from a config entry."""
    async_add_entities([PandaPWRCountdownTimer(entry.runtime_data, "countdown_time")])


class PandaPWRCountdownTimer(PandaPWREntity, NumberEntity):
    """Duration of the shutdown timer, in seconds; shows what is left while it runs."""

    _attr_device_class = NumberDeviceClass.DURATION
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX
    _attr_native_max_value = MAX_COUNTDOWN_SECONDS
    _attr_native_min_value = 0
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    @property
    def native_value(self) -> int | None:
        """Return the countdown reported by the device in the last poll."""
        return self.coordinator.data.get("countdown")

    async def async_set_native_value(self, value: float) -> None:
        """Send the new countdown to the device."""
        if not await self._api.set_countdown_timer(int(value)):
            msg = "Panda PWR did not accept the countdown change"
            raise HomeAssistantError(msg)
        self.coordinator.async_apply_write({"countdown": int(value)})

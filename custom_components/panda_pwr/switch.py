# Copyright (c) 2026 FixoLab
"""Switch platform for PandaPWR integration in Home Assistant."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COUNTDOWN_RUNNING,
    COUNTDOWN_STOPPED,
    DEFAULT_COUNTDOWN_SECONDS,
)
from .coordinator import PandaPWRConfigEntry, PandaPWREntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PandaPWRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform for PandaPWR."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            PowerSwitch(coordinator, "power_switch"),
            UsbSwitch(coordinator, "usb_switch"),
            ShutdownTimerSwitch(coordinator, "shutdown_timer"),
            AutoPoweroffSwitch(coordinator, "auto_poweroff_switch"),
        ]
    )


class PandaPWRSwitch(PandaPWREntity, SwitchEntity):
    """Switch that writes one output and shows it on every entity at once."""

    _attr_entity_category = EntityCategory.CONFIG

    async def _async_send(self, accepted: bool, changes: dict) -> None:  # noqa: FBT001
        """Raise when the device refused the command, otherwise show the change."""
        if not accepted:
            msg = f"Panda PWR did not accept the {self.name} change"
            raise HomeAssistantError(msg)
        self.coordinator.async_apply_write(changes)


class PowerSwitch(PandaPWRSwitch):
    """Mains output of the device."""

    @property
    def is_on(self) -> bool:
        """Return whether the output is on according to the last poll."""
        return self.coordinator.data.get("power_state") == 1

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the output."""
        await self._async_send(await self._api.set_power_state(1), {"power_state": 1})

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the output."""
        await self._async_send(await self._api.set_power_state(0), {"power_state": 0})


class UsbSwitch(PandaPWRSwitch):
    """USB output of the device."""

    @property
    def is_on(self) -> bool:
        """Return whether the output is on according to the last poll."""
        return self.coordinator.data.get("usb_state") == 1

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the output."""
        await self._async_send(await self._api.set_usb_state(1), {"usb_state": 1})

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the output."""
        await self._async_send(await self._api.set_usb_state(0), {"usb_state": 0})


class ShutdownTimerSwitch(PandaPWRSwitch):
    """
    Shutdown timer: cuts the mains output when the countdown reaches zero.

    It starts from the Countdown time value and, like the official web UI,
    turns the output on first when it is off.
    """

    _attr_entity_category = None

    @property
    def is_on(self) -> bool:
        """Return whether the timer is running or paused."""
        data = self.coordinator.data
        return (
            data.get("auto_poweroff") == 1
            and data.get("countdown_state", COUNTDOWN_STOPPED) != COUNTDOWN_STOPPED
        )

    async def async_turn_on(self, **_: Any) -> None:
        """Start the timer."""
        seconds = self.coordinator.data.get("countdown") or DEFAULT_COUNTDOWN_SECONDS
        power_off = self.coordinator.data.get("power_state") != 1
        changes = {
            "countdown": seconds,
            "countdown_state": COUNTDOWN_RUNNING,
            "auto_poweroff": 1,
        }
        if power_off:
            changes["power_state"] = 1
        await self._async_send(
            await self._api.start_countdown(seconds, power_on=power_off), changes
        )

    async def async_turn_off(self, **_: Any) -> None:
        """Stop the timer."""
        await self._async_send(
            await self._api.stop_countdown(),
            {"countdown_state": COUNTDOWN_STOPPED, "auto_poweroff": 0},
        )


class AutoPoweroffSwitch(PandaPWRSwitch):
    """
    Auto power-off flag; the countdown only runs while it is on.

    When bound to a Panda Touch, the device follows its Auto-Off countdown.
    """

    @property
    def is_on(self) -> bool:
        """Return whether auto power-off is enabled."""
        return self.coordinator.data.get("auto_poweroff") == 1

    async def async_turn_on(self, **_: Any) -> None:
        """Enable auto power-off."""
        await self._async_send(
            await self._api.set_auto_poweroff(1), {"auto_poweroff": 1}
        )

    async def async_turn_off(self, **_: Any) -> None:
        """Disable auto power-off."""
        await self._async_send(
            await self._api.set_auto_poweroff(0), {"auto_poweroff": 0}
        )

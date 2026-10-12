# Copyright (c) 2026 FixoLab
"""Button platform for PandaPWR integration in Home Assistant."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import PandaPWRApi
from .const import COUNTDOWN_PAUSED, COUNTDOWN_RUNNING
from .coordinator import PandaPWRConfigEntry, PandaPWRCoordinator, PandaPWREntity


@dataclass(frozen=True, kw_only=True)
class PandaPWRButtonDescription(ButtonEntityDescription):
    """Button sending one command; `changes` is the state it leaves behind."""

    press_fn: Callable[[PandaPWRApi], Awaitable[bool]]
    changes: dict = field(default_factory=dict)


BUTTONS = (
    PandaPWRButtonDescription(
        key="pause_shutdown_timer",
        press_fn=lambda api: api.pause_countdown(),
        changes={"countdown_state": COUNTDOWN_PAUSED, "auto_poweroff": 1},
    ),
    PandaPWRButtonDescription(
        key="resume_shutdown_timer",
        press_fn=lambda api: api.resume_countdown(),
        changes={"countdown_state": COUNTDOWN_RUNNING, "auto_poweroff": 1},
    ),
    # Destructive: disabled by default so a stray click cannot trigger them.
    PandaPWRButtonDescription(
        key="energy_usage_reset_button",
        press_fn=lambda api: api.reset_energy_usage(),
        changes={"ele": 0.0},
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    PandaPWRButtonDescription(
        key="factory_reset_button",
        press_fn=lambda api: api.do_factory_reset(),
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PandaPWRConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button platform for PandaPWR."""
    async_add_entities(
        PandaPWRButton(entry.runtime_data, description) for description in BUTTONS
    )


class PandaPWRButton(PandaPWREntity, ButtonEntity):
    """Button sending one command to the device."""

    entity_description: PandaPWRButtonDescription

    def __init__(
        self, coordinator: PandaPWRCoordinator, description: PandaPWRButtonDescription
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the command and show its effect."""
        if not await self.entity_description.press_fn(self._api):
            msg = f"Panda PWR did not accept {self.name}"
            raise HomeAssistantError(msg)
        if self.entity_description.changes:
            self.coordinator.async_apply_write(self.entity_description.changes)

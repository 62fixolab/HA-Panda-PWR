# Copyright (c) 2026 FixoLab
"""Button platform for PandaPWR integration in Home Assistant."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .api import PandaPWRApi
from .const import COUNTDOWN_PAUSED, COUNTDOWN_RUNNING, DOMAIN
from .coordinator import PandaPWRConfigEntry, PandaPWRCoordinator, PandaPWREntity


@dataclass(frozen=True, kw_only=True)
class PandaPWRButtonDescription(ButtonEntityDescription):
    """
    Button sending one command; `changes` is the state it leaves behind.

    A button with `confirm` only acts on a second press within
    CONFIRM_WINDOW, so neither a stray click nor a single automation call
    can trigger it.
    """

    press_fn: Callable[[PandaPWRApi], Awaitable[bool]]
    changes: dict = field(default_factory=dict)
    confirm: bool = False


CONFIRM_WINDOW = timedelta(seconds=10)


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
    # Destructive: disabled by default and confirmed with a second press.
    PandaPWRButtonDescription(
        key="energy_usage_reset_button",
        press_fn=lambda api: api.reset_energy_usage(),
        changes={"ele": 0.0},
        confirm=True,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    PandaPWRButtonDescription(
        key="factory_reset_button",
        press_fn=lambda api: api.do_factory_reset(),
        confirm=True,
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
        self._armed_until: datetime | None = None

    def _async_check_confirmed(self) -> None:
        """Arm on the first press and raise; let a second press in time through."""
        now = dt_util.utcnow()
        if self._armed_until is not None and now <= self._armed_until:
            self._armed_until = None
            return
        self._armed_until = now + CONFIRM_WINDOW
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="confirm_press",
            translation_placeholders={
                "name": str(self.name),
                "seconds": str(int(CONFIRM_WINDOW.total_seconds())),
            },
        )

    async def async_press(self) -> None:
        """Send the command and show its effect."""
        if self.entity_description.confirm:
            self._async_check_confirmed()
        if not await self.entity_description.press_fn(self._api):
            msg = f"Panda PWR did not accept {self.name}"
            raise HomeAssistantError(msg)
        if self.entity_description.changes:
            self.coordinator.async_apply_write(self.entity_description.changes)

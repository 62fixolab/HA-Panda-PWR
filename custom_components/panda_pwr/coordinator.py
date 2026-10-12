# Copyright (c) 2026 FixoLab
"""Data update coordinator for PandaPWR devices."""

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import PandaPWRApi, PandaPWRError
from .const import DOMAIN

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)
# The relay takes a moment to switch; reading back sooner returns the old state.
WRITE_SETTLE_SECONDS = 3


class PandaPWRCoordinator(DataUpdateCoordinator[dict]):
    """Poll the device once per interval and share the reply with every entity."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, api: PandaPWRApi
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self.device_id = f"pandapwr_{entry.data['ip_address']}"
        self._cancel_settle_refresh: Callable[[], None] | None = None

    @callback
    def async_apply_write(self, changes: dict) -> None:
        """Show an accepted write at once and read the device back once it settles."""
        self.async_set_updated_data({**self.data, **changes})
        if self._cancel_settle_refresh:
            self._cancel_settle_refresh()
        self._cancel_settle_refresh = async_call_later(
            self.hass, WRITE_SETTLE_SECONDS, self._async_settle_refresh
        )

    async def _async_settle_refresh(self, _now: datetime) -> None:
        self._cancel_settle_refresh = None
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Cancel the pending read-back before the entry unloads."""
        if self._cancel_settle_refresh:
            self._cancel_settle_refresh()
            self._cancel_settle_refresh = None
        await super().async_shutdown()

    async def _async_update_data(self) -> dict:
        """Fetch the latest state; a failure marks every entity unavailable."""
        try:
            return await self.api.get_data()
        except PandaPWRError as err:
            msg = f"Error communicating with Panda PWR: {err}"
            raise UpdateFailed(msg) from err


class PandaPWREntity(CoordinatorEntity[PandaPWRCoordinator]):
    """Base entity bound to a PandaPWR device."""

    def __init__(self, coordinator: PandaPWRCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._device_id = coordinator.device_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name="Panda PWR",
            manufacturer="Panda",
            model="PWR Device",
            sw_version="1.0",
        )

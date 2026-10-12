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
from .const import CONF_DEVICE_ID, CONF_IP_ADDRESS, DOMAIN, MANUFACTURER, MODEL

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)
# The relay takes a moment to switch; reading back sooner returns the old state.
WRITE_SETTLE_SECONDS = 3

type PandaPWRConfigEntry = ConfigEntry["PandaPWRCoordinator"]


class PandaPWRCoordinator(DataUpdateCoordinator[dict]):
    """Poll the device once per interval and share the reply with every entity."""

    def __init__(
        self, hass: HomeAssistant, entry: PandaPWRConfigEntry, api: PandaPWRApi
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self.entry = entry
        self.device_id: str = entry.data[CONF_DEVICE_ID]
        # Reply of /get_state (firmware, access point); filled once at setup.
        self.device_state: dict = {}
        self._cancel_settle_refresh: Callable[[], None] | None = None

    async def async_load_device_state(self) -> None:
        """Read firmware and access point details; older firmware may lack them."""
        try:
            self.device_state = await self.api.get_state()
        except PandaPWRError as err:
            _LOGGER.debug("Panda PWR did not report its device state: %s", err)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device registry entry shared by every entity."""
        firmware = str(self.device_state.get("fw_version", "")).split(" ", 1)[0]
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name="Panda PWR",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=firmware or None,
            configuration_url=f"http://{self.entry.data[CONF_IP_ADDRESS]}",
        )

    async def _async_update_data(self) -> dict:
        """Fetch the latest state; a failure marks every entity unavailable."""
        try:
            return await self.api.get_data()
        except PandaPWRError as err:
            msg = f"Error communicating with Panda PWR: {err}"
            raise UpdateFailed(msg) from err

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


class PandaPWREntity(CoordinatorEntity[PandaPWRCoordinator]):
    """Base entity bound to a PandaPWR device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PandaPWRCoordinator, key: str) -> None:
        """Initialize the entity; `key` is both its translation key and ID suffix."""
        super().__init__(coordinator)
        self._api = coordinator.api
        self._device_id = coordinator.device_id
        self._attr_translation_key = key
        self._attr_unique_id = f"{self._device_id}_{key}"
        self._attr_device_info = coordinator.device_info

# Copyright (c) 2026 FixoLab
"""Data update coordinator for PandaPWR devices."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import PandaPWRApi, PandaPWRError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


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

# Copyright (c) 2026 FixoLab
"""PandaPWR integration for Home Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import PandaPWRApi
from .const import DOMAIN

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PandaPWR from a config entry."""
    ip_address = entry.data["ip_address"]
    api = PandaPWRApi(ip_address)

    if not await api.test_connection():
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

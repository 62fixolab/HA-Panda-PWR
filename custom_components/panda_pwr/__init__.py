# Copyright (c) 2026 FixoLab
"""PandaPWR integration for Home Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PandaPWRApi
from .const import DOMAIN
from .coordinator import PandaPWRCoordinator

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
]

# Buttons used to share these unique IDs across every device.
LEGACY_BUTTON_UNIQUE_IDS = {
    "pandapwr_energy_usage_reset_button": "energy_usage_reset_button",
    "pandapwr_factory_reset_button": "factory_reset_button",
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PandaPWR from a config entry."""
    api = PandaPWRApi(async_get_clientsession(hass), entry.data["ip_address"])
    coordinator = PandaPWRCoordinator(hass, entry, api)

    await _async_migrate_button_unique_ids(hass, entry, coordinator.device_id)

    # Raises ConfigEntryNotReady when the device is offline, so HA retries later.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_migrate_button_unique_ids(
    hass: HomeAssistant, entry: ConfigEntry, device_id: str
) -> None:
    """Give the buttons per-device unique IDs, keeping their existing entity IDs."""

    @callback
    def _migrate(entity: er.RegistryEntry) -> dict | None:
        suffix = LEGACY_BUTTON_UNIQUE_IDS.get(entity.unique_id)
        if suffix is None:
            return None
        return {"new_unique_id": f"{device_id}_{suffix}"}

    await er.async_migrate_entries(hass, entry.entry_id, _migrate)

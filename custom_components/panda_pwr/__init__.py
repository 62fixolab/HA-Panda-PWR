# Copyright (c) 2026 FixoLab
"""PandaPWR integration for Home Assistant."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PandaPWRApi
from .const import CONF_DEVICE_ID, CONF_IP_ADDRESS, DOMAIN, legacy_device_id
from .coordinator import PandaPWRConfigEntry, PandaPWRCoordinator

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


async def async_setup_entry(hass: HomeAssistant, entry: PandaPWRConfigEntry) -> bool:
    """Set up PandaPWR from a config entry."""
    if CONF_DEVICE_ID not in entry.data:
        # Entries from 1.2.x derive the device ID from the IP; freeze it so a
        # later IP change keeps every entity and its history.
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_DEVICE_ID: legacy_device_id(entry.data[CONF_IP_ADDRESS]),
            },
        )

    api = PandaPWRApi(async_get_clientsession(hass), entry.data[CONF_IP_ADDRESS])
    coordinator = PandaPWRCoordinator(hass, entry, api)

    await _async_migrate_button_unique_ids(hass, entry, coordinator.device_id)

    # Raises ConfigEntryNotReady when the device is offline, so HA retries later.
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_load_device_state()
    _async_adopt_unique_id(hass, entry, coordinator.device_state.get("ap_ssid"))

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PandaPWRConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_shutdown()
    return unload_ok


@callback
def _async_adopt_unique_id(
    hass: HomeAssistant, entry: PandaPWRConfigEntry, ap_ssid: str | None
) -> None:
    """Give entries created before 1.3 the device's unique access point SSID."""
    if entry.unique_id or not ap_ssid:
        return
    if any(
        other.unique_id == ap_ssid
        for other in hass.config_entries.async_entries(DOMAIN)
        if other.entry_id != entry.entry_id
    ):
        return
    hass.config_entries.async_update_entry(entry, unique_id=ap_ssid)


async def _async_migrate_button_unique_ids(
    hass: HomeAssistant, entry: PandaPWRConfigEntry, device_id: str
) -> None:
    """Give the buttons per-device unique IDs, keeping their existing entity IDs."""

    @callback
    def _migrate(entity: er.RegistryEntry) -> dict | None:
        suffix = LEGACY_BUTTON_UNIQUE_IDS.get(entity.unique_id)
        if suffix is None:
            return None
        return {"new_unique_id": f"{device_id}_{suffix}"}

    await er.async_migrate_entries(hass, entry.entry_id, _migrate)

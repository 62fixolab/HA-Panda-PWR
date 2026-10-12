# Copyright (c) 2026 FixoLab
"""Diagnostics support for PandaPWR."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_DEVICE_ID, CONF_IP_ADDRESS
from .coordinator import PandaPWRConfigEntry

TO_REDACT = {
    CONF_IP_ADDRESS,
    CONF_DEVICE_ID,
    "unique_id",
    "ap_ssid",
    "ap_pwd",
    "sta_ip",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PandaPWRConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "device": async_redact_data(coordinator.device_state, TO_REDACT),
        "data": coordinator.data,
        "last_update_success": coordinator.last_update_success,
    }

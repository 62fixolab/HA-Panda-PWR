# Copyright (c) 2026 FixoLab
"""Diagnostics tests."""

import json

from homeassistant.core import HomeAssistant

from custom_components.panda_pwr.diagnostics import async_get_config_entry_diagnostics

from .conftest import AP_SSID, FakePandaPWR, make_entry, setup_entry


async def test_diagnostics_redact_secrets(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """Diagnostics include the device reply but never addresses or the AP password."""
    entry = await setup_entry(hass, make_entry(device, unique_id=AP_SSID))
    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["data"]["power"] == 96.6
    assert result["device"]["fw_version"].startswith("V1.0.0")
    assert result["last_update_success"] is True
    dumped = json.dumps(result)
    for secret in ("987654321", AP_SSID, device.host):
        assert secret not in dumped

# Copyright (c) 2026 FixoLab
"""Config flow tests: setup, duplicates and reconfiguration."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.panda_pwr.const import CONF_DEVICE_ID, CONF_IP_ADDRESS, DOMAIN

from .conftest import AP_SSID, FakePandaPWR, make_entry, setup_entry


async def start_user_flow(hass: HomeAssistant, ip_address: str) -> dict:
    """Open the user step and submit an IP address."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_IP_ADDRESS: ip_address}
    )


async def start_reconfigure_flow(hass: HomeAssistant, entry_id: str) -> dict:
    """Open the reconfigure step of an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry_id},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    return result


async def test_user_creates_entry(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """A reachable device creates an entry identified by its access point SSID."""
    result = await start_user_flow(hass, f" {device.host} ")
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_IP_ADDRESS: device.host,
        CONF_DEVICE_ID: f"pandapwr_{device.host}",
    }
    assert result["result"].unique_id == AP_SSID


async def test_user_cannot_connect(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """An unreachable address shows an error and lets the user retry."""
    await device.stop()
    result = await start_user_flow(hass, device.host)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_duplicate_ip(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """The same address cannot be added twice."""
    await setup_entry(hass, make_entry(device))
    result = await start_user_flow(hass, device.host)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_same_device_new_ip_updates_entry(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """Adding a known device at a new address moves the existing entry."""
    entry = make_entry(device, unique_id=AP_SSID)
    entry.add_to_hass(hass)
    old_host = device.host
    entry_data = {**entry.data, CONF_IP_ADDRESS: "127.0.0.1:1"}
    hass.config_entries.async_update_entry(entry, data=entry_data)

    result = await start_user_flow(hass, old_host)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_IP_ADDRESS] == old_host
    assert entry.data[CONF_DEVICE_ID] == f"pandapwr_{old_host}"


async def test_user_without_ssid(hass: HomeAssistant) -> None:
    """Firmware without /get_state still sets up, without a unique ID."""
    fake = FakePandaPWR(ap_ssid=None)
    await fake.start()
    try:
        result = await start_user_flow(hass, fake.host)
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["result"].unique_id is None
    finally:
        await fake.stop()


async def test_reconfigure_keeps_entities(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """A new IP keeps the frozen device ID, so entities keep their IDs."""
    entry = await setup_entry(hass, make_entry(device, unique_id=AP_SSID))
    original_device_id = entry.data[CONF_DEVICE_ID]
    port = device.port
    await device.stop()
    moved = FakePandaPWR()
    await moved.start()
    try:
        flow = await start_reconfigure_flow(hass, entry.entry_id)
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {CONF_IP_ADDRESS: moved.host}
        )
        await hass.async_block_till_done()
        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        assert entry.data[CONF_IP_ADDRESS] == moved.host
        assert entry.data[CONF_DEVICE_ID] == original_device_id
        assert moved.gets >= 1
    finally:
        await moved.stop()
        await device.start(port)


async def test_reconfigure_wrong_device(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """An address that answers with another SSID is refused."""
    entry = await setup_entry(hass, make_entry(device, unique_id=AP_SSID))
    other = FakePandaPWR("PandaPWR_OTHER")
    await other.start()
    try:
        flow = await start_reconfigure_flow(hass, entry.entry_id)
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {CONF_IP_ADDRESS: other.host}
        )
        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "wrong_device"
        assert entry.data[CONF_IP_ADDRESS] == device.host
    finally:
        await other.stop()


async def test_reconfigure_cannot_connect(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """An unreachable new address shows an error."""
    entry = await setup_entry(hass, make_entry(device, unique_id=AP_SSID))
    flow = await start_reconfigure_flow(hass, entry.entry_id)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"], {CONF_IP_ADDRESS: "127.0.0.1:1"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

# Copyright (c) 2026 FixoLab
"""Setup, unload and migration tests."""

import gc

import aiohttp
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.panda_pwr.const import CONF_DEVICE_ID, CONF_IP_ADDRESS, DOMAIN

from .conftest import AP_SSID, FakePandaPWR, make_entry, setup_entry


def open_sessions() -> int:
    """Count aiohttp sessions that are still open."""
    gc.collect()
    return sum(
        1
        for obj in gc.get_objects()
        if isinstance(obj, aiohttp.ClientSession) and not obj.closed
    )


async def test_setup_and_unload(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """The entry loads, reads the device once and unloads cleanly."""
    entry = await setup_entry(hass, make_entry(device))
    assert entry.state is ConfigEntryState.LOADED
    assert device.gets == 1

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_device_info(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """The device registry shows the real manufacturer, model and firmware."""
    entry = await setup_entry(hass, make_entry(device))
    (dev,) = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert dev.identifiers == {(DOMAIN, entry.data[CONF_DEVICE_ID])}
    assert dev.manufacturer == "BIGTREETECH"
    assert dev.model == "Panda PWR"
    assert dev.sw_version == "V1.0.0"
    assert dev.configuration_url == f"http://{device.host}"


async def test_offline_at_startup_retries(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """An unreachable device puts the entry in retry instead of a hard error."""
    await device.stop()
    entry = await setup_entry(hass, make_entry(device))
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_reloads_do_not_leak_sessions(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """Reloading keeps reusing Home Assistant's shared HTTP session."""
    entry = await setup_entry(hass, make_entry(device))
    before = open_sessions()
    for _ in range(20):
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
    assert open_sessions() == before


async def test_two_devices_get_all_entities(hass: HomeAssistant) -> None:
    """Every device gets its own full set of entities, buttons included."""
    first, second = FakePandaPWR("PandaPWR_A"), FakePandaPWR("PandaPWR_B")
    await first.start()
    await second.start()
    try:
        await setup_entry(hass, make_entry(first, "first"))
        await setup_entry(hass, make_entry(second, "second"))
        registry = er.async_get(hass)
        counts = [
            len(er.async_entries_for_config_entry(registry, entry_id))
            for entry_id in ("first", "second")
        ]
        assert counts[0] == counts[1] == 18
    finally:
        await first.stop()
        await second.stop()


async def test_legacy_entry_is_migrated(
    hass: HomeAssistant, device: FakePandaPWR
) -> None:
    """
    A 1.2.x entry keeps its entities.

    It gains a frozen device ID and the access point SSID as unique ID, and its
    shared button IDs become per device without changing their entity IDs.
    """
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_IP_ADDRESS: device.host}, entry_id="legacy"
    )
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    old_button = registry.async_get_or_create(
        "button",
        DOMAIN,
        "pandapwr_factory_reset_button",
        config_entry=entry,
        suggested_object_id="factory_reset",
    )
    old_sensor = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"pandapwr_{device.host}_power",
        config_entry=entry,
        suggested_object_id="power",
    )

    await setup_entry(hass, entry)

    assert entry.data[CONF_DEVICE_ID] == f"pandapwr_{device.host}"
    assert entry.unique_id == AP_SSID
    button = registry.async_get(old_button.entity_id)
    assert button.unique_id == f"pandapwr_{device.host}_factory_reset_button"
    assert registry.async_get(old_sensor.entity_id).unique_id == old_sensor.unique_id
    assert hass.states.get("sensor.power").state == "96.6"


async def test_unique_id_not_stolen(hass: HomeAssistant, device: FakePandaPWR) -> None:
    """A legacy entry does not take an SSID another entry already owns."""
    owner = MockConfigEntry(domain=DOMAIN, unique_id=AP_SSID, data={})
    owner.add_to_hass(hass)
    entry = await setup_entry(hass, make_entry(device))
    assert entry.unique_id is None
